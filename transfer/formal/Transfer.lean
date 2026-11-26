import Std
set_option maxRecDepth 100000
set_option maxHeartbeats 0
namespace Transfer

def pairMasks (n : Nat) : List Nat :=
  (List.range n).flatMap fun i => (List.range i).map fun j => 2^i + 2^j
def tripleMasks (n : Nat) : List Nat :=
  (List.range n).flatMap fun i => (List.range i).flatMap fun j =>
    (List.range j).map fun k => 2^i + 2^j + 2^k
def full (d s masks : List Nat) : Bool :=
  masks.all fun m =>
    let projected := s.map fun r => r &&& m
    d.all fun r => projected.contains (r &&& m)
def legal12 (d s : List Nat) : Bool :=
  decide s.Nodup && (s.length == 12) && s.all fun r => d.contains r
def hits (s bad : List Nat) : Nat := (s.filter fun r => bad.contains r).length

theorem coveredWitness (d s masks : List Nat) (m p : Nat) (cover : full d s masks = true)
    (hm : m ∈ masks) (hp : p ∈ d) : ∃ r ∈ s, r &&& m = p &&& m := by
  have step := List.all_eq_true.mp cover m hm
  have hit := List.all_eq_true.mp step p hp
  exact List.mem_map.mp (List.contains_iff_mem.mp hit)

theorem forcesReport (d s bad masks : List Nat) (m p : Nat) (cover : full d s masks = true)
    (hm : m ∈ masks) (hp : p ∈ d) (valid : ∀ r ∈ s, r ∈ d)
    (force : (d.all fun r => (r &&& m != p &&& m) || bad.contains r) = true) :
    ∃ r ∈ s, r ∈ bad := by
  obtain ⟨r, hr, he⟩ := coveredWitness d s masks m p cover hm hp
  have value := List.all_eq_true.mp force r (valid r hr)
  refine ⟨r,hr,?_⟩
  simpa [he] using value
theorem sizeBound (s t : List Nat) (hn : s.Nodup) (inc : ∀ a ∈ s, a ∈ t) :
    s.length ≤ t.length := by
  induction s generalizing t with
  | nil => simp
  | cons a l ih =>
    have hnod := List.nodup_cons.mp hn
    have ha := inc a (by simp)
    have sub : ∀ b ∈ l, b ∈ t.erase a := by
      intro b hb
      have hne : b ≠ a := by rintro rfl; exact hnod.1 hb
      apply (List.mem_erase_of_ne hne).mpr
      exact inc b (List.mem_cons_of_mem _ hb)
    have below := ih (t.erase a) hnod.2 sub
    rw [List.length_erase_of_mem ha] at below
    have hpos : 0 < t.length := List.length_pos_of_mem ha
    simp only [List.length_cons]
    omega

theorem partitionSize (s bad : List Nat) :
    hits s bad + (s.filter (fun r => !bad.contains r)).length = s.length := by
  unfold hits
  induction s with
  | nil => simp
  | cons a l ih =>
    cases h : bad.contains a <;>
      simp only [List.filter_cons,h,Bool.not_false,Bool.not_true,Bool.false_eq_true,
        if_true,if_false,List.length_cons] <;> omega

theorem capBad (s bad : List Nat) (hn : s.Nodup) : hits s bad ≤ bad.length := by
  apply sizeBound
  · exact hn.filter _
  · intro r hr
    exact List.contains_iff_mem.mp (List.mem_filter.mp hr).2

def classNum (ds : List (Nat × Nat)) (r : Nat) : Nat :=
  ds.findIdx fun x => (r &&& x.1) == x.2

theorem classWitness (d s bad masks : List Nat) (ds : List (Nat × Nat)) (code m p : Nat)
    (cover : full d s masks = true) (hm : m ∈ masks) (hp : p ∈ d)
    (valid : ∀ r ∈ s, r ∈ d)
    (cert : (d.all fun r => (r &&& m != p &&& m) ||
      ((!bad.contains r) && (classNum ds r == code))) = true) :
    code ∈ (s.filter (fun r => !bad.contains r)).map (classNum ds) := by
  obtain ⟨r,hr,he⟩ := coveredWitness d s masks m p cover hm hp
  have value := List.all_eq_true.mp cert r (valid r hr)
  have h : (bad.contains r = false) ∧ (classNum ds r = code) := by simpa [he] using value
  exact List.mem_map.mpr ⟨r,List.mem_filter.mpr ⟨hr,by rw [h.1]; decide⟩,h.2⟩

namespace ATM
def rows : List Nat := [0,2,4,6,8,10,12,14,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,34,36,38,40,42,44,46,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127]
def reported : List Nat := [2,4,6,8,10,12,14,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,34,36,38,40,42,44,46,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127]
def minRows : List Nat := [0,12,42,20,61,80,120,114,118,113,125,95]
def maxRows : List Nat := [12,6,34,42,24,62,53,120,124,85,113,91]
def pairs := pairMasks 7
theorem lowLegal : legal12 rows minRows = true := by decide +kernel
theorem lowFull : full rows minRows pairs = true := by decide +kernel
theorem lowHits : hits minRows reported = 11 := by decide +kernel
theorem highLegal : legal12 rows maxRows = true := by decide +kernel
theorem highFull : full rows maxRows pairs = true := by decide +kernel
theorem highHits : hits maxRows reported = 12 := by decide +kernel
theorem minimum (s : List Nat) (hn : s.Nodup) (v : ∀ r ∈ s, r ∈ rows) (l : s.length = 12) : 11 ≤ hits s reported := by
  have bound : (s.filter (fun r => !reported.contains r)).length ≤ (rows.filter (fun r => !reported.contains r)).length := by
    apply sizeBound _ _ (hn.filter _)
    intro r hr
    obtain ⟨hr,hs⟩ := List.mem_filter.mp hr
    exact List.mem_filter.mpr ⟨v r hr,hs⟩
  have census : (rows.filter (fun r => !reported.contains r)).length = 1 := by decide +kernel
  have part := partitionSize s reported
  omega
theorem maximum (s : List Nat) (h : s.length = 12) : hits s reported ≤ 12 := by
  have part := partitionSize s reported
  omega
end ATM
#print axioms ATM.lowLegal
#print axioms ATM.lowFull
#print axioms ATM.lowHits
#print axioms ATM.highLegal
#print axioms ATM.highFull
#print axioms ATM.highHits
#print axioms ATM.minimum
#print axioms ATM.maximum

namespace MinePump
def rows : List Nat := [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63]
def reported : List Nat := [1,9,17,25,33,41,49,57]
def minRows : List Nat := [2,19,18,12,8,20,13,63,59,58,37,21]
def maxRows : List Nat := [16,1,49,33,19,17,9,57,46,41,21,25]
def tripleRows : List Nat := [16,2,49,35,40,28,14,5,54,61,47,27]
def pairs := pairMasks 6
theorem lowLegal : legal12 rows minRows = true := by decide +kernel
theorem lowFull : full rows minRows pairs = true := by decide +kernel
theorem lowHits : hits minRows reported = 0 := by decide +kernel
theorem highLegal : legal12 rows maxRows = true := by decide +kernel
theorem highFull : full rows maxRows pairs = true := by decide +kernel
theorem highHits : hits maxRows reported = 8 := by decide +kernel
def triples := tripleMasks 6
theorem threeLegal : legal12 rows tripleRows = true := by decide +kernel
theorem threeFull : full rows tripleRows triples = true := by decide +kernel
theorem failureClass : (rows.all fun r => (reported.contains r == ((r &&& 7) == 1))) = true := by decide +kernel
theorem threeForces (s : List Nat) (v : ∀ r ∈ s, r ∈ rows) (h : full rows s triples = true) : ∃ r ∈ s, r ∈ reported := by
  exact forcesReport rows s reported triples 7 1 h (by decide) (by decide) v (by decide +kernel)
theorem maximum (s : List Nat) (hn : s.Nodup) : hits s reported ≤ 8 := by
  exact capBad s reported hn
theorem minimum (s : List Nat) : 0 ≤ hits s reported := Nat.zero_le _
end MinePump
#print axioms MinePump.lowLegal
#print axioms MinePump.lowFull
#print axioms MinePump.lowHits
#print axioms MinePump.highLegal
#print axioms MinePump.highFull
#print axioms MinePump.highHits
#print axioms MinePump.minimum
#print axioms MinePump.maximum
#print axioms MinePump.threeLegal
#print axioms MinePump.threeFull
#print axioms MinePump.failureClass
#print axioms MinePump.threeForces

namespace companies
def rows : List Nat := [0,1,2,3,4,5,8,9,16,17,18,19,20,21,24,25,32,33,34,35,36,37,40,41,48,49,50,51,52,53,56,57,64,65,66,67,68,69,72,73,80,81,82,83,84,85,88,89,96,97,98,99,100,101,104,105,112,113,114,115,116,117,120,121,128,129,130,131,132,133,136,137,144,145,146,147,148,149,152,153,160,161,162,163,164,165,168,169,176,177,178,179,180,181,184,185,192,193,194,195,196,197,200,201,208,209,210,211,212,213,216,217,224,225,226,227,228,229,232,233,240,241,242,243,244,245,248,249,256,257,258,259,260,261,264,265,272,273,274,275,276,277,280,281,288,289,290,291,292,293,296,297,304,305,306,307,308,309,312,313,320,321,322,323,324,325,328,329,336,337,338,339,340,341,344,345,352,353,354,355,356,357,360,361,368,369,370,371,372,373,376,377]
def reported : List Nat := [328,329,344,345,360,361,376,377]
def minRows : List Nat := [272,280,180,354,338,340,85,133,169,147,201,339]
def maxRows : List Nat := [64,290,328,360,228,344,376,277,185,329,211,377]
def pairs := pairMasks 9
theorem lowLegal : legal12 rows minRows = true := by decide +kernel
theorem lowFull : full rows minRows pairs = true := by decide +kernel
theorem lowHits : hits minRows reported = 0 := by decide +kernel
theorem highLegal : legal12 rows maxRows = true := by decide +kernel
theorem highFull : full rows maxRows pairs = true := by decide +kernel
theorem highHits : hits maxRows reported = 6 := by decide +kernel
theorem minimum (s : List Nat) : 0 ≤ hits s reported := Nat.zero_le _
def demands : List (Nat × Nat) := [(260,260),(132,132),(130,130),(258,258),(136,136),(384,0)]
theorem maximum (s : List Nat) (v : ∀ r ∈ s, r ∈ rows) (h : full rows s pairs = true) (l : s.length = 12) : hits s reported ≤ 6 := by
  have h0 := classWitness rows s reported pairs demands 0 260 260 h (by decide) (by decide) v (by decide +kernel)
  have h1 := classWitness rows s reported pairs demands 1 132 132 h (by decide) (by decide) v (by decide +kernel)
  have h2 := classWitness rows s reported pairs demands 2 130 130 h (by decide) (by decide) v (by decide +kernel)
  have h3 := classWitness rows s reported pairs demands 3 258 258 h (by decide) (by decide) v (by decide +kernel)
  have h4 := classWitness rows s reported pairs demands 4 136 136 h (by decide) (by decide) v (by decide +kernel)
  have h5 := classWitness rows s reported pairs demands 5 384 0 h (by decide) (by decide) v (by decide +kernel)
  have sub : ∀ i ∈ ([0,1,2,3,4,5] : List Nat), i ∈ (s.filter (fun r => !reported.contains r)).map (classNum demands) := by
    intro i hi
    simp at hi
    rcases hi with h|h|h|h|h|h <;> subst i <;> assumption
  have bound := sizeBound _ _ (by decide) sub
  simp only [List.length_cons,List.length_nil,List.length_map] at bound
  have part := partitionSize s reported
  omega
end companies
#print axioms companies.lowLegal
#print axioms companies.lowFull
#print axioms companies.lowHits
#print axioms companies.highLegal
#print axioms companies.highFull
#print axioms companies.highHits
#print axioms companies.minimum
#print axioms companies.maximum

namespace sudoku
def rows : List Nat := [0,1,2,3,16,17,18,19,48,49,50,51,56,57,58,59,60,61,62,63]
def reported : List Nat := [58,59,62,63]
def minRows : List Nat := [0,1,49,56,57,60,61,2,18,19,51,63]
def maxRows : List Nat := [0,48,1,57,61,2,18,51,58,59,62,63]
def pairs := pairMasks 6
theorem lowLegal : legal12 rows minRows = true := by decide +kernel
theorem lowFull : full rows minRows pairs = true := by decide +kernel
theorem lowHits : hits minRows reported = 1 := by decide +kernel
theorem highLegal : legal12 rows maxRows = true := by decide +kernel
theorem highFull : full rows maxRows pairs = true := by decide +kernel
theorem highHits : hits maxRows reported = 4 := by decide +kernel
theorem pairForces (s : List Nat) (v : ∀ r ∈ s, r ∈ rows) (h : full rows s pairs = true) : ∃ r ∈ s, r ∈ reported := by
  exact forcesReport rows s reported pairs 6 62 h (by decide) (by decide) v (by decide +kernel)
theorem maximum (s : List Nat) (hn : s.Nodup) : hits s reported ≤ 4 := by
  exact capBad s reported hn
theorem minimum (s : List Nat) (v : ∀ r ∈ s, r ∈ rows) (h : full rows s pairs = true) : 1 ≤ hits s reported := by
  obtain ⟨r,hr,br⟩ := pairForces s v h
  exact List.length_filter_pos_iff.mpr ⟨r,hr,List.contains_iff_mem.mpr br⟩
end sudoku
#print axioms sudoku.lowLegal
#print axioms sudoku.lowFull
#print axioms sudoku.lowHits
#print axioms sudoku.highLegal
#print axioms sudoku.highFull
#print axioms sudoku.highHits
#print axioms sudoku.minimum
#print axioms sudoku.maximum
#print axioms sudoku.pairForces
end Transfer
