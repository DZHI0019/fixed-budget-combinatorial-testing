import Mathlib.Data.ZMod.Basic
import Mathlib.Tactic

namespace SixGrid

abbrev F := ZMod 103
abbrev Point := F × F
def distinct3 {α : Type} (a b c : α) : Prop := a ≠ b ∧ a ≠ c ∧ b ≠ c
def separate (h : Point → F) (p q r : Point) := distinct3 (h p) (h q) (h r)
def first (p : Point) : F := p.1
def second (p : Point) : F := p.2
def diagonal (p : Point) : F := p.1 + p.2
def repair (p : Point) : F := 2 * p.1 + p.2
def corner (p q r : Point) : Prop :=
  p.1 = q.1 ∧ p.2 = r.2 ∧ diagonal q = diagonal r

theorem classify (p q r : Point) (hpq : p ≠ q) (hpr : p ≠ r) (hqr : q ≠ r)
    (h₁ : ¬separate first p q r) (h₂ : ¬separate second p q r)
    (h₃ : ¬separate diagonal p q r) :
    corner p q r ∨ corner p r q ∨ corner q p r ∨ corner q r p ∨
    corner r p q ∨ corner r q p := by
  simp only [separate, distinct3, first, second, diagonal] at h₁ h₂ h₃
  simp only [corner, diagonal]
  have conflict (u v : Point) (hne : u ≠ v) :
      ¬(u.1 = v.1 ∧ u.2 = v.2) ∧
      ¬(u.1 = v.1 ∧ u.1 + u.2 = v.1 + v.2) ∧
      ¬(u.2 = v.2 ∧ u.1 + u.2 = v.1 + v.2) := by
    constructor
    · exact fun ⟨ha,hb⟩ => hne (Prod.ext ha hb)
    constructor
    · rintro ⟨ha,hs⟩
      rw [ha] at hs
      exact hne (Prod.ext ha (add_left_cancel hs))
    · rintro ⟨hb,hs⟩
      rw [hb] at hs
      exact hne (Prod.ext (add_right_cancel hs) hb)
  have := conflict p q hpq
  have := conflict p r hpr
  have := conflict q r hqr
  grind only

def Fits {ι V : Type} (family : ι → Point → V) (p q r : Point) (x y z : V) : Prop :=
  ∃ t, family t p = x ∧ family t q = y ∧ family t r = z

theorem fits_swap {ι V : Type} {f : ι → Point → V} {p q r : Point} {x y z : V} :
    Fits f p r q x z y → Fits f p q r x y z :=
  fun ⟨t, hp, hr, hq⟩ => ⟨t, hp, hq, hr⟩

theorem fits_turn {ι V : Type} {f : ι → Point → V} {p q r : Point} {x y z : V} :
    Fits f q r p y z x → Fits f p q r x y z :=
  fun ⟨t, hq, hr, hp⟩ => ⟨t, hp, hq, hr⟩

/-- Once the three ordinary projections and the arithmetic-progression repair block
    have been checked on their small domains, the grid is three-way covering. -/
theorem lift_three {ι J K V : Type} [DecidableEq V]
    (family : ι → Point → V) (seed : J → F → V) (correction : K → F → V)
    (seed3 : ∀ a b c, distinct3 a b c → ∀ x y z, ∃ t, seed t a = x ∧ seed t b = y ∧ seed t c = z)
    (seed2 : ∀ a b, a ≠ b → ∀ x y, ∃ t, seed t a = x ∧ seed t b = y)
    (extra : ∀ a d : F, d ≠ 0 → ∀ x y z, distinct3 x y z →
      ∃ t, correction t a = x ∧ correction t (a+d) = y ∧ correction t (a+d+d) = z)
    (incl : ∀ h, h = first ∨ h = second ∨ h = diagonal → ∀ t, ∃ u, family u = seed t ∘ h)
    (inclExtra : ∀ t, ∃ u, family u = correction t ∘ repair)
    (p q r : Point) (hpq : p ≠ q) (hpr : p ≠ r) (hqr : q ≠ r) (x y z : V) :
    Fits family p q r x y z := by
  have regular (h : Point → F) (hi : h = first ∨ h = second ∨ h = diagonal)
      (sep : separate h p q r) : Fits family p q r x y z := by
    obtain ⟨t, ht⟩ := seed3 _ _ _ sep x y z
    obtain ⟨u, hu⟩ := incl h hi t
    exact ⟨u, by simpa [hu, Function.comp_def] using ht⟩
  by_cases h₁ : separate first p q r
  · exact regular first (Or.inl rfl) h₁
  by_cases h₂ : separate second p q r
  · exact regular second (Or.inr (Or.inl rfl)) h₂
  by_cases h₃ : separate diagonal p q r
  · exact regular diagonal (Or.inr (Or.inr rfl)) h₃
  have patch (a b c : Point) (ab : a ≠ b) (ac : a ≠ c)
      (hc : corner a b c) (i j k : V) : Fits family a b c i j k := by
    obtain ⟨h₁, h₂, h₃⟩ := hc
    have hba : b.2 ≠ a.2 := fun h => ab (Prod.ext h₁ h.symm)
    have hca : c.1 ≠ a.1 := fun h => ac (Prod.ext h.symm h₂)
    have hd : diagonal a ≠ diagonal b := by
      intro h
      apply hba
      unfold diagonal at h
      rw [h₁] at h
      exact (add_left_cancel h).symm
    by_cases hij : i = j
    · obtain ⟨t, ha, hb⟩ := seed2 a.1 c.1 (Ne.symm hca) i k
      obtain ⟨u, hu⟩ := incl first (Or.inl rfl) t
      exact ⟨u, by simpa [hu,first] using ha,
        by simpa [hu,first,← h₁,← hij] using ha, by simpa [hu,first] using hb⟩
    by_cases hik : i = k
    · obtain ⟨t, ha, hb⟩ := seed2 a.2 b.2 (Ne.symm hba) i j
      obtain ⟨u, hu⟩ := incl second (Or.inr (Or.inl rfl)) t
      exact ⟨u, by simpa [hu,second] using ha, by simpa [hu,second] using hb,
        by simpa [hu,second,← h₂,← hik] using ha⟩
    by_cases hjk : j = k
    · obtain ⟨t, ha, hb⟩ := seed2 (diagonal a) (diagonal b) hd i j
      obtain ⟨u, hu⟩ := incl diagonal (Or.inr (Or.inr rfl)) t
      exact ⟨u, by simpa [hu] using ha, by simpa [hu] using hb,
        by simpa [hu,← h₃,← hjk] using hb⟩
    let d := b.2-a.2
    have dn : d ≠ 0 := sub_ne_zero.mpr hba
    have step : repair b = repair a + d := by unfold repair d; rw [h₁]; ring
    have step' : repair c = repair a + d + d := by
      unfold diagonal at h₃
      unfold repair d
      linear_combination -2*h₃ + 2*(h₁.symm) + h₂
    obtain ⟨t, ha, hb, hc⟩ := extra (repair a) d dn i j k ⟨hij,hik,hjk⟩
    obtain ⟨u, hu⟩ := inclExtra t
    exact ⟨u, by simpa [hu] using ha, by simpa [hu,step] using hb,
      by simpa [hu,step'] using hc⟩
  rcases classify p q r hpq hpr hqr h₁ h₂ h₃ with hc | hc | hc | hc | hc | hc
  · exact patch p q r hpq hpr hc x y z
  · exact fits_swap (patch p r q hpr hpq hc x z y)
  · exact fits_turn (fits_swap (patch q p r (Ne.symm hpq) hqr hc y x z))
  · exact fits_turn (patch q r p hqr (Ne.symm hpq) hc y z x)
  · exact fits_turn (fits_turn (patch r p q (Ne.symm hpr) (Ne.symm hqr) hc z x y))
  · exact fits_swap (fits_turn (patch r q p (Ne.symm hqr) (Ne.symm hpr) hc z y x))
end SixGrid
