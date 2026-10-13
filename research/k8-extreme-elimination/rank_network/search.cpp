// Experimental exact-integer rank objective; heuristic search, not a lower bound.
#include <array>
#include <vector>
#include <random>
#include <cmath>
#include <iostream>
using Mat=std::array<int,9>;
struct Edge{int a,b,shift;};
int rank(Mat a,int m){
 bool nz=false;for(int i=0;i<m;i++)for(int j=0;j<m;j++)nz|=a[3*i+j]!=0;
 if(!nz)return 0;
 bool minor=false;for(int i=0;i<m;i++)for(int j=i+1;j<m;j++)for(int k=0;k<m;k++)for(int l=k+1;l<m;l++)minor|=a[3*i+k]*a[3*j+l]!=a[3*i+l]*a[3*j+k];
 if(!minor)return 1;if(m==2)return 2;
 int det=a[0]*(a[4]*a[8]-a[5]*a[7])-a[1]*(a[3]*a[8]-a[5]*a[6])+a[2]*(a[3]*a[7]-a[4]*a[6]);return det?3:2;
}
int main(){
 int cases;std::cin>>cases;std::mt19937 rng(20261013);std::uniform_real_distribution<double> U(0,1);
 for(int c=0;c<cases;c++){
  int n,m,ne,W,steps,restarts;std::cin>>n>>m>>ne>>W>>steps>>restarts;
  std::vector<Edge> edges(ne);std::vector<std::vector<int>> incident(n);
  for(int i=0;i<ne;i++){auto &e=edges[i];std::cin>>e.a>>e.b>>e.shift;incident[e.a].push_back(i);if(e.a!=e.b)incident[e.b].push_back(i);}
  std::vector<Mat> state(n),best(n);int bc=W*m, nontrivial=0;long accepted=0,proposed=0;
  auto ecost=[&](int i){auto&e=edges[i];Mat d{};for(int k=0;k<9;k++)d[k]=state[e.b][k]-state[e.a][k];for(int k=0;k<m;k++)d[3*k+k]+=e.shift;return rank(d,m);};
  for(int run=0;run<restarts;run++){
   state=best;int cost=bc;
   for(int t=0;t<steps;t++){
    int v=1+rng()%(n-1);Mat before=state[v];int old=0;for(int i:incident[v])old+=ecost(i);
    int u[3]={},z[3]={};for(int j=0;j<m;j++){u[j]=int(rng()%3)-1;z[j]=int(rng()%3)-1;}
    bool change=false,ok=true;for(int i=0;i<m;i++)for(int j=0;j<m;j++){int &x=state[v][3*i+j];x+=u[i]*z[j];change|=u[i]*z[j]!=0;ok&=std::abs(x)<=4;}
    if(!change||!ok){state[v]=before;continue;}proposed++;
    int fresh=0;for(int i:incident[v])fresh+=ecost(i);int delta=fresh-old;
    double temp=0.04+0.75*(1.0-double(t)/steps);
    if(delta<=0 || U(rng)<std::exp(-delta/temp)){cost+=delta;accepted++;}
    else {state[v]=before;continue;}
    if(cost<bc){bc=cost;best=state;std::cerr<<"improved case "<<c<<" cost "<<bc<<" budget "<<W*m<<"\n";}
   }
  }
  std::cout<<c<<" "<<bc<<" "<<proposed<<" "<<accepted<<"\n";
  for(auto&a:best){for(int x:a)std::cout<<x<<" ";std::cout<<"\n";}
 }
}
