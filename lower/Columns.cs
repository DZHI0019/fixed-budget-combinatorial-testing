using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;

partial class Search {
    int[][] wordsByOption; int[] subsetSizes, accum, pick, bestPick;
    int high,tie; double jitter;
    // Fix thirteen columns. Each possible choice of the remaining column is a
    // partition of the twelve rows into bins, one bin per categorical value.
    // Each bin contributes the number of distinct (other field,value) labels
    // observed in precisely that subset of rows.
    void Visit(int slot) {
        if(slot==12) {
            int quality=0;
            for(int v=0;v<accum.Length;v++)quality+=subsetSizes[accum[v]];
            quality=quality*1000+(jitter>0?(int)Math.Min(1000*jitter, -Math.Log(Math.Max(rng.NextDouble(),1e-12))*130*jitter):0);
            if(quality>high){high=quality;tie=1;pick.CopyTo(bestPick,0);}
            else if(quality==high && rng.Next(++tie)==0)pick.CopyTo(bestPick,0);
            return;
        }
        foreach(int v in wordsByOption[slot]) {
            accum[v]|=1<<slot;pick[slot]=v;
            Visit(slot+1);
            accum[v]^=1<<slot;
        }
    }
    void ColumnStep(int col, double temperature) {
        ulong mask=15UL<<(4*col);
        wordsByOption=new int[B][];
        int maxValue=0;
        for(int i=0;i<B;i++) {
            var options=new List<int>();
            for(int v=0;v<8;v++) if(ids.ContainsKey((keys[s[i]]&~mask)|((ulong)v<<(4*col)))) {
                options.Add(v);maxValue=Math.Max(maxValue,v);
            }
            wordsByOption[i]=options.ToArray();
        }
        subsetSizes=new int[4096];
        int total=0;
        for(int f=0;f<14;f++) if(f!=col) {
            int[] groups=new int[8];
            for(int i=0;i<B;i++) groups[(keys[s[i]]>>(4*f))&15]|=1<<i;
            foreach(int m in groups)if(m!=0){subsetSizes[m]++;total++;}
        }
        for(int bit=1;bit<4096;bit*=2)
            for(int start=0;start<4096;start+=2*bit)
                for(int j=start;j<start+bit;j++)subsetSizes[j+bit]+=subsetSizes[j];
        for(int m=0;m<2048;m++) {
            int x=subsetSizes[m];subsetSizes[m]=total-subsetSizes[4095^m];subsetSizes[4095^m]=total-x;
        }
        high=-1;tie=0;accum=new int[maxValue+1];pick=new int[B];bestPick=new int[B];
        jitter=temperature;
        Visit(0);
        for(int i=0;i<B;i++)s[i]=ids[(keys[s[i]]&~mask)|((ulong)bestPick[i]<<(4*col))];
        score=Evaluate(-1,0,-1,0);Capture();
    }
    public void Columns(int restarts,int iterations,string path) {
        var starts=File.ReadLines(path).Select(x=>x.Split(' ').Select(int.Parse).ToArray()).ToArray();
        int[] cols={0,1,2,3,4,5,9,10,11,12,13};
        for(int run=0;run<restarts;run++){
            if(run%2!=0)best.CopyTo(s,0);
            else starts[rng.Next(starts.Length)].CopyTo(s,0);
            for(int pass=0;pass<iterations;pass++) {
                rng.Shuffle(cols);
                double temp = (pass%5<2 ? 6.0 : pass%5==2?2.0:0.0);
                foreach(int col in cols)ColumnStep(col,temp);
                if(pass%4==0)Polish();
            }
        }
        Console.WriteLine("Final: "+record);
    }
}
