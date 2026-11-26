"""Generate the exact row codes and ground certificates from a separately parsed benchmark."""
import itertools
from pathlib import Path
from verify_extremes import HERE, run, EXPECTED, SIX

def term(rows):return "["+",".join(map(str,rows))+"]"

def render():
    records=run()
    lines=["import Std","set_option maxRecDepth 100000","set_option maxHeartbeats 0",
           "namespace Transfer",""]
    lines.extend("""
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
""".strip().splitlines())
    lines.extend((HERE/"formal_base.txt").read_text(encoding="utf-8").splitlines())
    for name,d in records.items():
        lines.extend(["","namespace "+name])
        for key in ("rows","reported","minRows","maxRows","tripleRows"):
            if key in d:lines.append(f"def {key} : List Nat := {term(d[key])}")
        n=len(d['features'])
        lines.append(f"def pairs := pairMasks {n}")
        for key,tag,cnt in zip(["minRows","maxRows"],["low","high"],EXPECTED[name]):
            lines.extend([f"theorem {tag}Legal : legal12 rows {key} = true := by decide +kernel",
                          f"theorem {tag}Full : full rows {key} pairs = true := by decide +kernel",
                          f"theorem {tag}Hits : hits {key} reported = {cnt} := by decide +kernel"])
        if name=="MinePump":
            lines.extend([f"def triples := tripleMasks {n}",
                "theorem threeLegal : legal12 rows tripleRows = true := by decide +kernel",
                "theorem threeFull : full rows tripleRows triples = true := by decide +kernel",
                "theorem failureClass : (rows.all fun r => (reported.contains r == ((r &&& 7) == 1))) = true := by decide +kernel",
                "theorem threeForces (s : List Nat) (v : ∀ r ∈ s, r ∈ rows) (h : full rows s triples = true) : ∃ r ∈ s, r ∈ reported := by",
                "  exact forcesReport rows s reported triples 7 1 h (by decide) (by decide) v (by decide +kernel)"])
        if name=="sudoku":
            m=sum(2**d['features'].index(f) for f in ["EXTENDEDSUDOKU","GENERATOR"])
            p=next(r for r in d['rows'] if (r&m)==m)
            lines.extend(["theorem pairForces (s : List Nat) (v : ∀ r ∈ s, r ∈ rows) (h : full rows s pairs = true) : ∃ r ∈ s, r ∈ reported := by",
                f"  exact forcesReport rows s reported pairs {m} {p} h (by decide) (by decide) v (by decide +kernel)"])
        if name in {"sudoku","MinePump"}:
            lines.extend([f"theorem maximum (s : List Nat) (hn : s.Nodup) : hits s reported ≤ {EXPECTED[name][1]} := by",
                "  exact capBad s reported hn"])
        if EXPECTED[name][0]==0:
            lines.append("theorem minimum (s : List Nat) : 0 ≤ hits s reported := Nat.zero_le _")
        if name=="sudoku":
            lines.extend(["theorem minimum (s : List Nat) (v : ∀ r ∈ s, r ∈ rows) (h : full rows s pairs = true) : 1 ≤ hits s reported := by",
                "  obtain ⟨r,hr,br⟩ := pairForces s v h",
                "  exact List.length_filter_pos_iff.mpr ⟨r,hr,List.contains_iff_mem.mpr br⟩"])
        if name=="ATM":
            lines.extend(["theorem minimum (s : List Nat) (hn : s.Nodup) (v : ∀ r ∈ s, r ∈ rows) (l : s.length = 12) : 11 ≤ hits s reported := by",
                "  have bound : (s.filter (fun r => !reported.contains r)).length ≤ (rows.filter (fun r => !reported.contains r)).length := by",
                "    apply sizeBound _ _ (hn.filter _)",
                "    intro r hr",
                "    obtain ⟨hr,hs⟩ := List.mem_filter.mp hr",
                "    exact List.mem_filter.mpr ⟨v r hr,hs⟩",
                "  have census : (rows.filter (fun r => !reported.contains r)).length = 1 := by decide +kernel",
                "  have part := partitionSize s reported","  omega",
                "theorem maximum (s : List Nat) (h : s.length = 12) : hits s reported ≤ 12 := by",
                "  have part := partitionSize s reported","  omega"])
        if name=="companies":
            masks=[]
            proofs=[]
            for i,(a,b,x,y) in enumerate(SIX):
                u=2**d["features"].index(a); v=2**d["features"].index(b)
                mask,val=u+v,u*x+v*y
                source=next(r for r in d['rows'] if r&mask==val)
                masks.append(f"({mask},{val})")
                proofs.append(f"  have h{i} := classWitness rows s reported pairs demands {i} {mask} {source} h (by decide) (by decide) v (by decide +kernel)")
            lines.extend(["def demands : List (Nat × Nat) := ["+",".join(masks)+"]",
                "theorem maximum (s : List Nat) (v : ∀ r ∈ s, r ∈ rows) (h : full rows s pairs = true) (l : s.length = 12) : hits s reported ≤ 6 := by",
                *proofs,
                "  have sub : ∀ i ∈ ([0,1,2,3,4,5] : List Nat), i ∈ (s.filter (fun r => !reported.contains r)).map (classNum demands) := by",
                "    intro i hi","    simp at hi","    rcases hi with h|h|h|h|h|h <;> subst i <;> assumption",
                "  have bound := sizeBound _ _ (by decide) sub",
                "  simp only [List.length_cons,List.length_nil,List.length_map] at bound",
                "  have part := partitionSize s reported","  omega"])
        lines.extend([f"end {name}"])
        for label in ["lowLegal","lowFull","lowHits","highLegal","highFull","highHits","minimum","maximum"]:
            lines.append(f"#print axioms {name}.{label}")
        if name=="MinePump":
            for label in ["threeLegal","threeFull","failureClass","threeForces"]:
                lines.append(f"#print axioms {name}.{label}")
        if name=="sudoku":
            lines.append("#print axioms sudoku.pairForces")
    lines.append("end Transfer")
    return "\n".join(lines)+"\n"


if __name__=="__main__":
    path=HERE/"formal"/"Transfer.lean"
    path.parent.mkdir(exist_ok=True)
    path.write_text(render(),encoding="utf-8",newline="\n")
