import CensusData
set_option maxRecDepth 1000000
set_option maxHeartbeats 0
namespace TestBudget
theorem chosen_score : score chosen = 642 := by decide +kernel
theorem certified_interval :
    (∃ s : Finset Row, s.card ≤ 12 ∧ (∀ r ∈ s, inCensus r) ∧ (covered s).card = 642) ∧
    (∀ s : Finset Row, s.card ≤ 12 → (∀ r ∈ s, inCensus r) → (covered s).card ≤ 648) := by
  constructor
  · refine ⟨chosen.toFinset, ?_, ?_, (score_eq chosen).symm.trans chosen_score⟩
    · exact (List.toFinset_card_le chosen).trans (by decide)
    · intro r hr
      exact Or.inl (List.mem_toFinset.mp hr)
  · exact fun s hs _ => budget_upper s hs
end TestBudget
#print axioms TestBudget.certified_interval
