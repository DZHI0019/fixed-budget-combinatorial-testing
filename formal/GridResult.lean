import GridFacts
namespace SixGrid

abbrev Test := Fin 6 ⊕ ((Fin 3 × Fin 618) ⊕ Fin 480)

def direction (g : Fin 3) : Point → F :=
  if g = 0 then first else if g = 1 then second else diagonal

def plan : Test → Point → V
  | .inl v, _ => v
  | .inr (.inl (g,t)), p => seed ⟨t.val+6, by omega⟩ (direction g p)
  | .inr (.inr t), p => corr t (repair p)

theorem includes_seed (g : Fin 3) (t : Fin 624) :
    ∃ u, plan u = seed t ∘ direction g := by
  by_cases h : t.val < 6
  · refine ⟨.inl ⟨t,h⟩, ?_⟩
    funext p
    exact (constant_rows t h _).symm
  · let j : Fin 618 := ⟨t.val-6, by omega⟩
    refine ⟨.inr (.inl (g,j)), ?_⟩
    funext p
    have eq : (⟨j.val+6, by omega⟩ : Fin 624) = t := Fin.ext (by dsimp [j]; omega)
    change seed _ _ = seed t _
    rw [eq]

theorem complete (p q r : Point) (hpq : p ≠ q) (hpr : p ≠ r) (hqr : q ≠ r)
    (x y z : V) : ∃ t : Test, plan t p = x ∧ plan t q = y ∧ plan t r = z := by
  apply lift_three plan seed corr all_seed two_seed all_repair _ _ p q r hpq hpr hqr x y z
  · intro g hg t
    rcases hg with rfl | rfl | rfl
    · exact includes_seed 0 t
    · exact includes_seed 1 t
    · exact includes_seed 2 t
  · exact fun t => ⟨.inr (.inr t), rfl⟩

theorem size_and_strength :
    Fintype.card Test = 2340 ∧ Fintype.card Point = 10609 ∧
    ∀ p q r : Point, p ≠ q → p ≠ r → q ≠ r → ∀ x y z : V,
      ∃ t : Test, plan t p = x ∧ plan t q = y ∧ plan t r = z := by
  refine ⟨?_, ?_, complete⟩
  · simp [Test]
  · simp [Point, F]

end SixGrid
#print axioms SixGrid.lift_three
#print axioms SixGrid.size_and_strength
