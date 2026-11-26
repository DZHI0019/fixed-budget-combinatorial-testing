import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Data.Finset.Card
import Mathlib.Data.Finset.Range
import Mathlib.Tactic

namespace TestBudget

/-- The first integer is an ordinary-item bitset, the second stores 21 nine-bit slots.
    A slot with value 511 is padding. Codes 0..364 name the special items. -/
abbrev Row := Nat × Nat

def slot (r : Row) (i : Nat) : Nat := (r.2 >>> (9 * i)) % 512

def rare (r : Row) : Finset Nat :=
  (((Finset.range 21).image (fun j => 396 + slot r j)).filter (· < 761))

def ordinary (r : Row) : Finset Nat :=
  (Finset.range 396).filter (fun j => r.1.testBit j)

def hit (r : Row) : Finset Nat := ordinary r ∪ rare r

def covered (s : Finset Row) : Finset Nat := s.biUnion hit

theorem rare_card (r : Row) : (rare r).card ≤ 21 := by
  unfold rare
  exact (Finset.card_le_card (Finset.filter_subset _ _)).trans
    (Finset.card_image_le.trans (by simp))

theorem budget_upper (s : Finset Row) (h : s.card ≤ 12) : (covered s).card ≤ 648 := by
  have incl : covered s ⊆ Finset.range 396 ∪ s.biUnion rare := by
    intro x hx
    obtain ⟨r, hr, hhit⟩ := Finset.mem_biUnion.mp hx
    rcases Finset.mem_union.mp hhit with hc | hs
    · exact Finset.mem_union_left _ (Finset.mem_of_mem_filter _ hc)
    · exact Finset.mem_union_right _ (Finset.mem_biUnion.mpr ⟨r, hr, hs⟩)
  have hu := Finset.card_le_card incl
  have hv := Finset.card_union_le (Finset.range 396) (s.biUnion rare)
  have hw := Finset.card_biUnion_le_card_mul s rare 21 (fun r _ => rare_card r)
  simp only [Finset.card_range] at hv
  omega

/-- A small executable membership test for exactly the same semantics. -/
def contains (r : Row) (i : Nat) : Bool :=
  if i < 396 then r.1.testBit i
  else i < 761 && (List.range 21).any (fun j => i == 396 + slot r j)

theorem contains_iff (r : Row) (i : Nat) : contains r i = true ↔ i ∈ hit r := by
  simp only [contains, hit, ordinary, rare, Finset.mem_union, Finset.mem_filter,
    Finset.mem_image, Finset.mem_range]
  by_cases h : i < 396
  · simp [h]
    omega
  · simp only [h, if_false, false_and, false_or, Bool.and_eq_true, decide_eq_true_eq,
      List.any_eq_true, List.mem_range, beq_iff_eq]
    constructor
    · rintro ⟨hi, j, hj, he⟩
      exact ⟨⟨j, hj, he.symm⟩, hi⟩
    · rintro ⟨⟨j, hj, he⟩, hi⟩
      exact ⟨hi, j, hj, he.symm⟩

def score (rs : List Row) : Nat :=
  ((List.range 761).filter (fun i => rs.any (fun r => contains r i))).length

theorem score_eq (rs : List Row) : score rs = (covered rs.toFinset).card := by
  let good := (List.range 761).filter (fun i => rs.any (fun r => contains r i))
  have nodup : good.Nodup := (List.nodup_range).filter _
  have eqset : good.toFinset = covered rs.toFinset := by
    ext i
    simp only [good, List.mem_toFinset, List.mem_filter, List.mem_range, List.any_eq_true,
      contains_iff, covered, Finset.mem_biUnion]
    constructor
    · exact fun h => h.2
    · rintro ⟨r, hr, hi⟩
      refine ⟨?_, r, hr, hi⟩
      rcases Finset.mem_union.mp hi with ho | hs
      · have : i < 396 := Finset.mem_range.mp (Finset.mem_of_mem_filter _ ho)
        omega
      · exact (Finset.mem_filter.mp hs).2
  rw [← eqset, List.toFinset_card_of_nodup nodup]
  rfl

end TestBudget
