import Transfer
namespace Transfer.Table
set_option maxHeartbeats 0
set_option maxRecDepth 100000
def requests (s masks : List Nat) : Nat :=
  ((masks.map fun m => ((s.map fun r => r &&& m).eraseDups).length)).sum
def ATM_plan : List Nat := [4, 6, 42, 20, 56, 60, 55, 120, 82, 118, 89, 125]
def ATM_greedy : List Nat := [8, 32, 14, 42, 21, 29, 51, 59, 122, 89, 113, 119]
theorem ATM_table :
  ATM.rows.length = 80 ∧ requests ATM.rows ATM.pairs = 82 ∧
  legal12 ATM.rows ATM_plan = true ∧ legal12 ATM.rows ATM_greedy = true ∧
  full ATM.rows ATM_plan ATM.pairs = true ∧ full ATM.rows ATM_greedy ATM.pairs = true ∧
  hits ATM_plan ATM.reported = 12 ∧ hits ATM_greedy ATM.reported = 12 := by decide +kernel
#print axioms ATM_table
def MinePump_plan : List Nat := [2, 36, 24, 9, 54, 61, 53, 46, 38, 42, 27, 22]
def MinePump_greedy : List Nat := [2, 51, 49, 34, 56, 62, 53, 46, 37, 41, 23, 29]
theorem MinePump_table :
  MinePump.rows.length = 64 ∧ requests MinePump.rows MinePump.pairs = 60 ∧
  legal12 MinePump.rows MinePump_plan = true ∧ legal12 MinePump.rows MinePump_greedy = true ∧
  full MinePump.rows MinePump_plan MinePump.pairs = true ∧ full MinePump.rows MinePump_greedy MinePump.pairs = true ∧
  hits MinePump_plan MinePump.reported = 1 ∧ hits MinePump_greedy MinePump.reported = 2 := by decide +kernel
#print axioms MinePump_table
def companies_plan : List Nat := [136, 276, 324, 232, 226, 212, 37, 25, 51, 259, 195, 377]
def companies_greedy : List Nat := [168, 194, 324, 244, 101, 89, 137, 259, 179, 309, 361, 345]
theorem companies_table :
  companies.rows.length = 192 ∧ requests companies.rows companies.pairs = 140 ∧
  legal12 companies.rows companies_plan = true ∧ legal12 companies.rows companies_greedy = true ∧
  full companies.rows companies_plan companies.pairs = true ∧ full companies.rows companies_greedy companies.pairs = true ∧
  hits companies_plan companies.reported = 1 ∧ hits companies_greedy companies.reported = 2 := by decide +kernel
#print axioms companies_table
def sudoku_plan : List Nat := [0, 48, 1, 17, 56, 60, 61, 2, 18, 58, 59, 63]
def sudoku_greedy : List Nat := [0, 48, 1, 49, 57, 61, 2, 50, 3, 19, 58, 62]
theorem sudoku_table :
  sudoku.rows.length = 20 ∧ requests sudoku.rows sudoku.pairs = 54 ∧
  legal12 sudoku.rows sudoku_plan = true ∧ legal12 sudoku.rows sudoku_greedy = true ∧
  full sudoku.rows sudoku_plan sudoku.pairs = true ∧ full sudoku.rows sudoku_greedy sudoku.pairs = true ∧
  hits sudoku_plan sudoku.reported = 3 ∧ hits sudoku_greedy sudoku.reported = 2 := by decide +kernel
#print axioms sudoku_table
theorem aggregate_detection :
  hits ATM_plan ATM.reported + hits MinePump_plan MinePump.reported + hits companies_plan companies.reported + hits sudoku_plan sudoku.reported = 17 ∧
  hits ATM_greedy ATM.reported + hits MinePump_greedy MinePump.reported + hits companies_greedy companies.reported + hits sudoku_greedy sudoku.reported = 18 := by decide +kernel
theorem threeway_assignment_count : requests MinePump.rows MinePump.triples = 160 := by decide +kernel
#print axioms aggregate_detection
#print axioms threeway_assignment_count
end Transfer.Table
