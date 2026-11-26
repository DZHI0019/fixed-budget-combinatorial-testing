import Transfer

set_option maxRecDepth 100000
set_option maxHeartbeats 0

namespace Transfer.MinePump.Minimum

abbrev Request := Nat × Nat

def agrees (r : Nat) (t : Request) : Bool := (r &&& t.1) == (t.2 &&& t.1)

-- Complete bounded set-cover decision procedure. At every node a solution
-- must supply some candidate for the first remaining request.
def search : Nat → List Nat → List Request → Bool
  | _, _, [] => true
  | 0, _, _ :: _ => false
  | n+1, candidates, t :: ts => candidates.any fun r =>
      agrees r t && search n candidates (ts.filter fun x => !agrees r x)

theorem searchComplete (fuel : Nat) (candidates s : List Nat) (ts : List Request)
    (within : s.length ≤ fuel) (valid : ∀ r ∈ s, r ∈ candidates)
    (covers : ∀ t ∈ ts, ∃ r ∈ s, agrees r t = true) :
    search fuel candidates ts = true := by
  induction fuel generalizing s ts with
  | zero =>
    cases ts with
    | nil => rfl
    | cons t ts =>
      obtain ⟨r, hr, _⟩ := covers t (by simp)
      have hpos : 0 < s.length := List.length_pos_of_mem hr
      omega
  | succ n ih =>
    cases ts with
    | nil => rfl
    | cons t ts =>
      obtain ⟨r,hr,hit⟩ := covers t (by simp)
      apply List.any_eq_true.mpr
      refine ⟨r,valid r hr,?_⟩
      simp only [hit, Bool.true_and]
      apply ih (s := s.erase r)
      · rw [List.length_erase_of_mem hr]
        omega
      · intro q hq
        exact valid q (List.mem_of_mem_erase hq)
      · intro u hu
        obtain ⟨hu, miss⟩ := List.mem_filter.mp hu
        obtain ⟨q,hq,ok⟩ := covers u (List.mem_cons_of_mem _ hu)
        have neq : q ≠ r := by
          rintro rfl
          simp [ok] at miss
        exact ⟨q,(List.mem_erase_of_ne neq).mpr hq,ok⟩

-- Demands for the other five switches on either side of the first switch.
def requests (b : Nat) : List Request := (List.range 5).flatMap fun i =>
  (List.range i).flatMap fun j =>
    let x := 2^(i+1)
    let y := 2^(j+1)
    [(1+x+y,b),(1+x+y,b+x),(1+x+y,b+y),(1+x+y,b+x+y)]

def part (s : List Nat) (b : Nat) : List Nat := s.filter fun r => (r % 2) == b

def validRequests (b : Nat) : Bool := (requests b).all fun t =>
  triples.contains t.1 && rows.contains t.2 &&
    rows.all fun r => !agrees r t || ((r % 2) == b)

theorem actualSixCube : rows = List.range 64 := by decide +kernel
theorem sideZero : validRequests 0 = true := by decide +kernel
theorem sideOne : validRequests 1 = true := by decide +kernel

theorem partitionDemands (s : List Nat) (b : Nat) (cert : validRequests b = true)
    (valid : ∀ r ∈ s, r ∈ rows) (cov : full rows s triples = true) :
    ∀ t ∈ requests b, ∃ r ∈ part s b, agrees r t = true := by
  intro t ht
  have props := List.all_eq_true.mp cert t ht
  simp only [Bool.and_eq_true] at props
  obtain ⟨⟨hm,hp⟩,guard⟩ := props
  obtain ⟨r,hr,he⟩ := coveredWitness rows s triples t.1 t.2 cov
    (List.contains_iff_mem.mp hm) (List.contains_iff_mem.mp hp)
  have eqn : agrees r t = true := beq_iff_eq.mpr he
  have g := List.all_eq_true.mp guard r (valid r hr)
  exact ⟨r,List.mem_filter.mpr ⟨hr,by simpa [eqn] using g⟩,eqn⟩

theorem sideMinimum (s : List Nat) (b : Nat) (cert : validRequests b = true)
    (noFive : search 5 (part rows b) (requests b) = false)
    (valid : ∀ r ∈ s, r ∈ rows) (cov : full rows s triples = true) :
    6 ≤ (part s b).length := by
  by_cases short : (part s b).length ≤ 5
  · have contradiction := searchComplete 5 (part rows b) (part s b) (requests b) short
      (fun r hr => by
        obtain ⟨mem,tag⟩ := List.mem_filter.mp hr
        exact List.mem_filter.mpr ⟨valid r mem,tag⟩)
      (partitionDemands s b cert valid cov)
    simp [noFive] at contradiction
  · omega

theorem sumPartition (s : List Nat) : (part s 0).length + (part s 1).length = s.length := by
  induction s with
  | nil => rfl
  | cons a s ih =>
    unfold part at *
    have h : a % 2 = 0 ∨ a % 2 = 1 := by omega
    rcases h with h|h <;>
      simp only [List.filter_cons,h,beq_self_eq_true,Nat.reduceBEq,Bool.false_eq_true,
        if_true,if_false,List.length_cons] <;> omega

-- Finite negative certificates are verified by kernel reduction.
theorem noZeroFive : search 5 (part rows 0) (requests 0) = false := by decide +kernel
theorem noOneFive : search 5 (part rows 1) (requests 1) = false := by decide +kernel

theorem globalMinimum (s : List Nat) (valid : ∀ r ∈ s, r ∈ rows)
    (cov : full rows s triples = true) : 12 ≤ s.length := by
  have h0 := sideMinimum s 0 sideZero noZeroFive valid cov
  have h1 := sideMinimum s 1 sideOne noOneFive valid cov
  have h := sumPartition s
  omega

theorem attained : legal12 rows tripleRows = true ∧ full rows tripleRows triples = true :=
  ⟨threeLegal,threeFull⟩

#print axioms globalMinimum
#print axioms attained
end Transfer.MinePump.Minimum
