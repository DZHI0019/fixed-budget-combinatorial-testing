import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Data.Fintype.BigOperators
import Mathlib.Tactic

/-! Exact deficit accounting for a selection of twelve configurations.
    Interactions have distinct labels, ordinary or marked. Rows are indexed
    by their positions, so the theorem even permits repeated configurations. -/
namespace CoverageLoss

abbrev Family (k : Nat) := Fin 12 → Finset (Fin k)

/-- Multiplicity of a particular interaction in the twelve selected rows. -/
def multiplicity {k : Nat} (a : Family k) (x : Fin k) : Nat :=
  ∑ r, if x ∈ a r then 1 else 0

/-- Cardinality of the union, expressed as the number of labels with a hit. -/
def touched {k : Nat} (a : Family k) : Nat :=
  ∑ x, if multiplicity a x = 0 then 0 else 1

theorem touched_is_union_card {k : Nat} (a : Family k) :
    touched a = (Finset.univ.biUnion a).card := by
  unfold touched
  calc
    _ = ∑ x : Fin k, (if x ∈ Finset.univ.biUnion a then 1 else 0 : Nat) := by
      apply Finset.sum_congr rfl
      intro x _
      have hz : multiplicity a x = 0 ↔ x ∉ Finset.univ.biUnion a := by
        simp [multiplicity]
      by_cases hx : x ∈ Finset.univ.biUnion a <;> simp [hz, hx]
    _ = _ := by
      simp
      congr 1
      ext x
      simp

def score (ordinary : Family 396) (marked : Family 365) : Nat :=
  touched ordinary + touched marked

def missed (ordinary : Family 396) : Nat :=
  ∑ x, if multiplicity ordinary x = 0 then 1 else 0

def repeats (marked : Family 365) : Nat :=
  ∑ x, (multiplicity marked x - 1)

def room (marked : Family 365) : Nat :=
  ∑ r, (21 - (marked r).card)

private theorem ordinary_partition (a : Family 396) :
    touched a + missed a = 396 := by
  unfold touched missed
  rw [← Finset.sum_add_distrib]
  calc
    _ = ∑ _ : Fin 396, (1 : Nat) := Finset.sum_congr rfl (by
      intro x _
      by_cases h : multiplicity a x = 0 <;> simp [h])
    _ = 396 := by simp

private theorem marked_partition (a : Family 365) :
    touched a + repeats a = ∑ r, (a r).card := by
  unfold touched repeats
  rw [← Finset.sum_add_distrib]
  calc
    _ = ∑ x, multiplicity a x := Finset.sum_congr rfl (by
      intro x _
      by_cases h : multiplicity a x = 0
      · simp [h]
      · simp [h]; omega)
    _ = ∑ r, ∑ x : Fin 365, (if x ∈ a r then 1 else 0 : Nat) := Finset.sum_comm
    _ = _ := by simp

private theorem slots_partition (a : Family 365) (cap : ∀ r, (a r).card ≤ 21) :
    (∑ r, (a r).card) + room a = 252 := by
  unfold room
  rw [← Finset.sum_add_distrib]
  calc
    _ = ∑ _ : Fin 12, (21 : Nat) := Finset.sum_congr rfl (by
      intro r _
      have h := cap r
      omega)
    _ = 252 := by simp

/-- Every unit of lost coverage has exactly one of these three causes. -/
theorem deficit_identity (a : Family 396) (b : Family 365)
    (cap : ∀ r, (b r).card ≤ 21) :
    score a b + missed a + repeats b + room b = 648 := by
  have h₁ := ordinary_partition a
  have h₂ := marked_partition b
  have h₃ := slots_partition b cap
  unfold score
  omega

theorem exact_loss (a : Family 396) (b : Family 365)
    (cap : ∀ r, (b r).card ≤ 21) :
    648 - score a b = missed a + repeats b + room b := by
  have h := deficit_identity a b cap
  omega

/-- A branch bearing disjoint certified lower bounds for the three budgets
    can meet 643 only if their combined loss is at most five. -/
theorem required_for_643 (a : Family 396) (b : Family 365)
    (cap : ∀ r, (b r).card ≤ 21) (goal : 643 ≤ score a b)
    {m d s : Nat} (hm : m ≤ missed a) (hd : d ≤ repeats b) (hs : s ≤ room b) :
    m + d + s ≤ 5 := by
  have h := deficit_identity a b cap
  omega

theorem exclude_643 (a : Family 396) (b : Family 365)
    (cap : ∀ r, (b r).card ≤ 21)
    {m d s : Nat} (hm : m ≤ missed a) (hd : d ≤ repeats b) (hs : s ≤ room b)
    (excess : 5 < m + d + s) : score a b ≤ 642 := by
  have h := deficit_identity a b cap
  omega

#print axioms touched_is_union_card
#print axioms deficit_identity
#print axioms exact_loss
#print axioms required_for_643
#print axioms exclude_643

end CoverageLoss
