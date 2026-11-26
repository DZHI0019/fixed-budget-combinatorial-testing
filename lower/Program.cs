using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Numerics;
using System.Runtime.CompilerServices;

// Each bit corresponds to a feasible pair. The row ID lookup enforces feasibility
// even when whole groups of dependent fields are exchanged.
partial class Search {
    const int B=12, W=12;
    readonly Random rng;
    readonly ulong[] keys, masks;
    readonly Dictionary<ulong,int> ids = new();
    readonly ulong[] groups;
    readonly int[] s = new int[B], best = new int[B];
    readonly int seed; readonly string output;
    readonly ulong[] scratch = new ulong[W];
    const ulong DbMask=0xfffUL << 24;
    Dictionary<ulong,int[]> dbRows;
    int[] locked;
    int score, record;

    public Search(string input,string output,int seed) {
        this.output=output; this.seed=seed; rng=new Random(seed);
        using var reader=new BinaryReader(File.OpenRead(input));
        int n=reader.ReadInt32(); keys=new ulong[n]; masks=new ulong[n*W];
        for(int i=0;i<n;i++) {
            keys[i]=reader.ReadUInt64(); ids.Add(keys[i],i);
            for(int w=0;w<W;w++) masks[i*W+w]=reader.ReadUInt64();
        }
        for(int i=0;i<B;i++) best[i]=reader.ReadInt32();
        dbRows=Enumerable.Range(0,n).GroupBy(i=>keys[i]&DbMask).ToDictionary(g=>g.Key,g=>g.ToArray());
        best.CopyTo(s,0); record=score=Evaluate(-1,0,-1,0);
        var groupIndices = new List<int[]>();
        for(int i=0;i<14;i++) groupIndices.Add(new[]{i});
        foreach(var a in new int[][]{new[]{6,7,8},new[]{7,8},new[]{6,7,8,10},
                    new[]{3,6,7,8,10},new[]{1,2},new[]{1,2,4,5,11},
                    new[]{2,11},new[]{1,2,6,7,8},new[]{1,4,5},new[]{1,2,11}})
            groupIndices.Add(a);
        groups=groupIndices.Select(g=>g.Aggregate(0UL,(a,i)=>a | (15UL << (i*4)))).ToArray();
    }
    int Evaluate(int a,int ra,int b,int rb) {
        Array.Clear(scratch);
        for(int i=0;i<B;i++){
            int ptr=W*(i==a?ra:i==b?rb:s[i]);
            for(int w=0;w<W;w++) scratch[w]|=masks[ptr+w];
        }
        int v=0;
        for(int w=0;w<W;w++)v+=BitOperations.PopCount(scratch[w]);
        return v;
    }
    void Capture(){
        if(score<=record)return;
        record=score; s.CopyTo(best,0);
        string result=record+" "+string.Join(" ",best);
        Console.WriteLine($"{seed} {result}");
        File.WriteAllText(output,result+Environment.NewLine);
    }
    void Polish(){
        for(int pass=0;pass<3;pass++){
            int prev=score;
            for(int k=0;k<B;k++){
                Array.Clear(scratch);
                for(int i=0;i<B;i++) if(i!=k)
                    for(int w=0;w<W;w++)scratch[w]|=masks[s[i]*W+w];
                int high=-1,chosen=0,ties=0;
                for(int r=0;r<keys.Length;r++){
                    if(locked!=null && ((keys[r]^keys[locked[k]])&DbMask)!=0)continue;
                    int gain=0;
                    for(int w=0;w<W;w++)gain+=BitOperations.PopCount(masks[r*W+w]&~scratch[w]);
                    if(gain>high){high=gain;chosen=r;ties=1;}
                    else if(gain==high && rng.Next(++ties)==0)chosen=r;
                }
                s[k]=chosen; score=Evaluate(-1,0,-1,0); Capture();
            }
            if(score<=prev)break;
        }
    }
    public void Fixed(string cases,int perCase,int length) {
        foreach(string line in File.ReadLines(cases)) {
            locked=line.Split(' ').Select(int.Parse).ToArray();
            locked.CopyTo(s,0); score=Evaluate(-1,0,-1,0);Polish();
            int[] local=(int[])s.Clone(); int localBest=score;
            for(int rep=0;rep<perCase;rep++) {
                local.CopyTo(s,0);score=localBest;
                double start=rep%3==0?2.4:rep%3==1?1.4:0.95;
                for(int it=0;it<length;it++) {
                    int a=rng.Next(B),b=rng.Next(B-1); if(b>=a)b++;
                    int old=s[a],other=s[b],ra,rb=other;
                    int mode=rng.Next(100);
                    int[] valid=dbRows[keys[old]&DbMask];
                    if(mode>=92) {
                        ra=valid[rng.Next(valid.Length)];
                    } else {
                        ulong mask=groups[rng.Next(groups.Length)];
                        if(rng.Next(6)==0)mask |= groups[rng.Next(groups.Length)];
                        mask&=~DbMask;
                        ulong source=mode<50?keys[other]:keys[valid[rng.Next(valid.Length)]];
                        ulong diff=(keys[old]^source)&mask;
                        if(diff==0 || !ids.TryGetValue(keys[old]^diff,out ra))continue;
                        if(mode<26 && !ids.TryGetValue(keys[other]^diff,out rb))continue;
                    }
                    int ns=Evaluate(a,ra,b,rb);
                    if(ns<score && rng.NextDouble()>=Math.Exp((ns-score)/(start*(1.0-0.94*it/length))))continue;
                    s[a]=ra;s[b]=rb;score=ns;Capture();
                    if(score>localBest){localBest=score;s.CopyTo(local,0);}
                }
                Polish();
                if(score>localBest){localBest=score;s.CopyTo(local,0);}
            }
        }
        Console.WriteLine("Final: "+record);
    }
    public void Anneal(int rounds,int length){
        for(int round=0;round<rounds;round++){
            best.CopyTo(s,0); score=record;
            double start=new double[]{1.2,1.9,0.9,1.5,2.3}[round%5];
            for(int it=0;it<length;it++){
                int a=rng.Next(B),b=rng.Next(B-1); if(b>=a)b++;
                int old=s[a],other=s[b];
                ulong mask=groups[rng.Next(groups.Length)];
                if(rng.Next(6)==0)mask |= groups[rng.Next(groups.Length)];
                int mode=rng.Next(100);
                ulong source=mode<60?keys[other]:keys[rng.Next(keys.Length)];
                ulong diff=(keys[old]^source)&mask;
                if(diff==0 || !ids.TryGetValue(keys[old]^diff,out int ra))continue;
                int rb=other;
                if(mode<42 && !ids.TryGetValue(keys[other]^diff,out rb))continue;
                int ns=Evaluate(a,ra,b,rb);
                if(ns<score){
                    double temperature=start*(1.0-0.94*it/length);
                    if(rng.NextDouble()>=Math.Exp((ns-score)/temperature))continue;
                }
                s[a]=ra;s[b]=rb;score=ns;Capture();
            }
            Polish();
            if(record>=648)return;
        }
        Console.WriteLine("Final: "+record);
    }
    static void Main(string[] args){
        var instance=new Search(args[0],args[1],int.Parse(args[2]));
        if(args.Length==7)instance.Columns(int.Parse(args[3]),int.Parse(args[4]),args[5]);
        else if(args.Length==6)instance.Fixed(args[5],int.Parse(args[3]),int.Parse(args[4]));
        else instance.Anneal(int.Parse(args[3]),int.Parse(args[4]));
    }
}
