using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
class Join{
 static int[] fields,db=new int[12],n=new int[14];
 static int[,] domain=new int[12,14], values=new int[15,12];static int[,,,] kind=new int[14,14,8,8];
 static Dictionary<int,int>[,] prefix;
 static int[,] key;static long nodes;
 static int[,,,] deficiency=new int[14,8,14,13];
 static int[,] future;
 // Counts at a fixed value of a finished column reserve unavoidable losses
 // against each unfinished column. All these interactions are disjoint.
 static void setFuture(int stage,int f,int start){
   int[] counts=new int[n[f]];for(int r=0;r<12;r++)counts[values[f,r]]++;
   for(int q=start;q<fields.Length;q++)for(int a=0;a<n[f];a++)
       future[stage,q]+=deficiency[f,a,fields[q],counts[a]];
 }
 static int pop(ulong n){n-=((n>>1)&0x5555555555555555UL);n=(n&0x3333333333333333UL)+((n>>2)&0x3333333333333333UL);return (int)((((n+(n>>4))&0x0f0f0f0f0f0f0f0fUL)*0x0101010101010101UL)>>56);}
 class Task {
   // A task is one entire column. Use two 64-bit blocks for the feasible
   // labels between this column and the previously assigned columns.
   public int p,cap,f; public int[] old; public ulong[,] add0=new ulong[12,4],add1=new ulong[12,4];public ulong[] end0=new ulong[13],end1=new ulong[13];
   public ulong w0,w1,u0,u1;public int[,] penalty =new int[12,4];public int[] possible=new int[12], minRest=new int[13];
   public Task(int depth,int rem){
     p=depth;f=fields[p];cap=rem;old=(new int[]{6,7,8}).Concat(fields.Take(p)).ToArray();int m=0;
     foreach(int j in old) for(int a=0;a<n[f];a++)for(int b=0;b<n[j];b++){
       int w=kind[f,j,a,b];if(w==0)continue;bool hi=(m>=64);if(m>=128)throw new Exception("need third mask"); ulong bit=1UL<<(m++);
       if(hi){if(w==2)w1|=bit;else u1|=bit;}else{if(w==2)w0|=bit;else u0|=bit;}
       for(int r=0;r<12;r++) if(values[j,r]==b){if(hi)add1[r,a]|=bit;else add0[r,a]|=bit;}
     }
     for(int r=11;r>=0;r--){int min=100;end0[r]=end0[r+1];end1[r]=end1[r+1];
       for(int v=0;v<n[f];v++){int k=(key[p,r]<<2)+v;int cost;
         if(!prefix[p,db[r]].TryGetValue(k,out cost))continue;penalty[r,v]=cost;min=Math.Min(min,cost);possible[r]|=1<<v;
         end0[r]|=add0[r,v];end1[r]|=add1[r,v];
       }minRest[r]=minRest[r+1]+min;
     }
   }
   public bool go(int r,int loss,int slack,ulong s0,ulong s1){
     int lb=loss+pop(u0&~(s0|end0[r]))+pop(u1&~(s1|end1[r]));
     if(lb+slack+minRest[r]>cap)return false;
     if(r==12){nodes++;
       for(int j=p+1;j<fields.Length;j++)future[p+1,j]=future[p,j];
       setFuture(p+1,f,p+1);
       int nextReserve=0;
       for(int j=p+1;j<fields.Length;j++)nextReserve+=future[p,j];
       return solve(p+1,cap-lb+nextReserve);
     }
     for(int v=0;v<n[f];v++)if((possible[r]&(1<<v))!=0){
       if(r>0 && db[r]==db[r-1] && key[p,r]==key[p,r-1] && v<values[f,r-1])continue;
       ulong m0=add0[r,v],m1=add1[r,v];int dupl=pop(s0&m0&w0)+pop(s1&m1&w1);
       key[p+1,r]=(key[p,r]<<2)+v;values[f,r]=v;
       if(go(r+1,loss+dupl,slack+penalty[r,v],s0|m0,s1|m1))return true;
     }
     return false;
   }
 }
 static bool solve(int p,int rem){
    if(p==fields.Length)return true;
    int reserve=0;for(int q=p+1;q<fields.Length;q++)reserve+=future[p,q];
    if(rem<reserve+future[p,p])return false;
    return new Task(p,rem-reserve).go(0,0,0,0,0);
 }
 static int dbval(int g,int i){for(int v=0;;v++)if((domain[g,i]&(1<<v))!=0)return v;}
 static int intern(){int s=0;for(int i=6;i<9;i++)for(int j=i+1;j<9;j++)for(int a=0;a<n[i];a++)for(int b=0;b<n[j];b++){int c=0;foreach(int g in db)if(dbval(g,i)==a&&dbval(g,j)==b)c++;int w=kind[i,j,a,b];if(w==2)s+=Math.Max(0,c-1);if(w==1&&c==0)s++;}return s;}
 public static void Main(string[] args){
   int target=int.Parse(args[0]);
   if(target<int.Parse(File.ReadAllText("threshold.txt")))throw new ArgumentException("Regenerate histograms for this lower target");
   fields=args[1].Split(',').Select(int.Parse).ToArray();
   if(fields.Length!=fields.Distinct().Count()||fields.Any(i=>i<0||i>=14||(i>=6&&i<=8)))throw new ArgumentException("Choose different non-database fields");
   int gap=648-target;key=new int[fields.Length+1,12];
   int[] raw=File.ReadAllLines("instance.dat").Select(int.Parse).ToArray();int p=0;for(int i=0;i<14;i++)n[i]=raw[p++];
   for(int g=0;g<12;g++)for(int i=0;i<14;i++)domain[g,i]=raw[p++];
   for(int i=0;i<14;i++)for(int j=i+1;j<14;j++)for(int a=0;a<n[i];a++)for(int b=0;b<n[j];b++)kind[i,j,a,b]=kind[j,i,b,a]=raw[p++];
   for(int i=0;i<14;i++)for(int a=0;a<n[i];a++)for(int j=0;j<14;j++){
      int w=0,u=0;for(int b=0;b<n[j];b++){if(kind[i,j,a,b]==1)u++;if(kind[i,j,a,b]==2)w++;}
      for(int m=0;m<=12;m++)deficiency[i,a,j,m]=Math.Max(0,u-m)+(u==0?Math.Max(0,m-w):0);
   }
   prefix=new Dictionary<int,int>[fields.Length,12];for(int l=0;l<fields.Length;l++)for(int g=0;g<12;g++)prefix[l,g]=new Dictionary<int,int>();
   foreach(var line in File.ReadAllLines("types.dat")){var t=line.Split(' ').Select(int.Parse).ToArray();int k=0;
     for(int l=0;l<fields.Length;l++){k=(k<<2)+t[2+fields[l]];int prev;var m=prefix[l,t[0]];if(!m.TryGetValue(k,out prev)||t[1]<prev)m[k]=t[1];}}
   foreach(var line in File.ReadAllLines(args.Length>=3?args[2]:"top.txt")){
     var h=line.Split(' ').Select(int.Parse).ToArray();if(h[0]<648-gap)continue;int r=0;for(int g=0;g<12;g++)for(int i=0;i<h[g+1];i++)db[r++]=g;
     future=new int[fields.Length+1,fields.Length];for(int i=6;i<9;i++){for(int t=0;t<12;t++)values[i,t]=dbval(db[t],i);setFuture(0,i,0);}nodes=0;
     bool ok=solve(0,gap-intern());Console.WriteLine(line+" => "+ok+" nodes "+nodes);
     if(ok)File.WriteAllLines("witness"+string.Join("-",h)+".txt",Enumerable.Range(0,12).Select(t=>string.Join(" ",Enumerable.Range(0,14).Select(i=>values[i,t]))));
   }
 }
}
