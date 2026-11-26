import GridData
namespace SixGrid
set_option maxHeartbeats 0

abbrev Table := Array (Array Nat)
abbrev V := Fin 6

def support (t : Table) (a : Fin 103) (x : V) : Nat := (t[a.val]!)[x.val]!
def cell (t : Table) {n : Nat} (r : Fin n) (a : Fin 103) : V :=
  if (support t a 0).testBit r then 0 else
  if (support t a 1).testBit r then 1 else
  if (support t a 2).testBit r then 2 else
  if (support t a 3).testBit r then 3 else
  if (support t a 4).testBit r then 4 else 5

def consistent (t : Table) (n : Nat) : Prop :=
  ∀ (a : Fin 103) (x : V) (r : Fin n),
    (support t a x).testBit r = true → cell t r a = x

def overlap (t : Table) (n : Nat) (a b c : Fin 103) (x y z : V) : Nat :=
  (2^n-1) &&& support t a x &&& support t b y &&& support t c z

theorem witness {t : Table} {n : Nat} (h : consistent t n)
    {a b c : Fin 103} {x y z : V} (hit : overlap t n a b c x y z ≠ 0) :
    ∃ r : Fin n, cell t r a = x ∧ cell t r b = y ∧ cell t r c = z := by
  have hb : ∃ i, (overlap t n a b c x y z).testBit i = true := by
    by_contra! hzero
    apply hit
    exact Nat.eq_of_testBit_eq (fun i => by simpa using hzero i)
  obtain ⟨i, hi⟩ := hb
  simp only [overlap, Nat.testBit_and, Nat.testBit_two_pow_sub_one, Bool.and_eq_true,
    decide_eq_true_eq] at hi
  let r : Fin n := ⟨i, hi.1.1.1⟩
  exact ⟨r, h a x r hi.1.1.2, h b y r hi.1.2, h c z r hi.2⟩

def seed (r : Fin 624) (a : F) : V := cell seedTable r a
def corr (r : Fin 480) (a : F) : V := cell repairTable r a

-- These finite predicates use Lean's compiled decision procedure. The generic
-- geometry and the implication from certified bit intersections are kernel proofs.
theorem consistent_seed : consistent seedTable 624 := by
  unfold consistent
  native_decide
theorem consistent_corr : consistent repairTable 480 := by
  unfold consistent
  native_decide

theorem first_six : ∀ (i : Fin 6) (b : Fin 103),
    cell seedTable (n := 624) ⟨i,by omega⟩ b = i := by decide +kernel

theorem constant_rows (r : Fin 624) (h : r.val < 6) (a : F) : seed r a = ⟨r.val,h⟩ :=
  first_six ⟨r,h⟩ a

theorem checked_sorted : ∀ a b c : Fin 103, a < b → b < c → ∀ x y z : V,
    overlap seedTable 624 a b c x y z ≠ 0 := by native_decide

theorem all_seed (a b c : F) (ds : distinct3 a b c) (x y z : V) :
    ∃ r, seed r a = x ∧ seed r b = y ∧ seed r c = z := by
  have get (i j k : Fin 103) (hij : i < j) (hjk : j < k) (u v w : V) :=
    witness consistent_seed (checked_sorted i j k hij hjk u v w)
  change distinct3 (α := Fin 103) a b c at ds
  rcases lt_or_gt_of_ne ds.1 with hab | hba
  · rcases lt_or_gt_of_ne ds.2.2 with hbc | hcb
    · exact get a b c hab hbc x y z
    · rcases lt_or_gt_of_ne ds.2.1 with hac | hca
      · obtain ⟨t,h₁,h₂,h₃⟩ := get a c b hac hcb x z y
        exact ⟨t,h₁,h₃,h₂⟩
      · obtain ⟨t,h₁,h₂,h₃⟩ := get c a b hca hab z x y
        exact ⟨t,h₂,h₃,h₁⟩
  · rcases lt_or_gt_of_ne ds.2.1 with hac | hca
    · obtain ⟨t,h₁,h₂,h₃⟩ := get b a c hba hac y x z
      exact ⟨t,h₂,h₁,h₃⟩
    · rcases lt_or_gt_of_ne ds.2.2 with hbc | hcb
      · obtain ⟨t,h₁,h₂,h₃⟩ := get b c a hbc hca y z x
        exact ⟨t,h₃,h₁,h₂⟩
      · obtain ⟨t,h₁,h₂,h₃⟩ := get c b a hcb hba z y x
        exact ⟨t,h₃,h₂,h₁⟩

theorem two_seed (a b : F) (ne : a ≠ b) (x y : V) :
    ∃ r, seed r a = x ∧ seed r b = y := by
  have anyThird (i j : Fin 103) : ∃ k : Fin 103, i ≠ k ∧ j ≠ k := by
    by_contra! bad
    have h₀ := bad 0
    have h₁ := bad 1
    have h₂ := bad 2
    have e₁ : (0 : Fin 103) ≠ 1 := by decide
    have e₂ : (0 : Fin 103) ≠ 2 := by decide
    have e₃ : (1 : Fin 103) ≠ 2 := by decide
    grind only
  obtain ⟨k,hak,hbk⟩ := anyThird a b
  obtain ⟨t,h₁,h₂,_⟩ := all_seed a b k ⟨ne,hak,hbk⟩ x y 0
  exact ⟨t,h₁,h₂⟩

theorem checked_repair : ∀ a d : F, d ≠ 0 → ∀ x y z : V,
    (x ≠ y ∧ x ≠ z ∧ y ≠ z) →
    overlap repairTable 480 a (a+d) (a+d+d) x y z ≠ 0 := by native_decide

theorem all_repair (a d : F) (hd : d ≠ 0) (x y z : V) (h : distinct3 x y z) :
    ∃ t, corr t a = x ∧ corr t (a+d) = y ∧ corr t (a+d+d) = z :=
  witness consistent_corr (checked_repair a d hd x y z h)

end SixGrid
