#include "student.h"
#include <stdio.h>
#include <string.h>
#include <stdint.h>
#define CHECK(x) do { if (!(x)) { fprintf(stderr,"FAIL line %d: %s\n",__LINE__,#x); return 1; } } while(0)
#define N 4
int main(void) {
    uint32_t c[N]={0,2,2,3}, a[N]={3,0,2,0};
    uint32_t original_c[N], original_a[N];
    memcpy(original_c,c,sizeof c); memcpy(original_a,a,sizeof a);
    uint32_t sent[N+1]={0}, workspace[N+1]={0};
    uint64_t backlog[N+1]={0}, remaining=999;
    size_t delays[N+1]={0}, times[N+1]={0}, completed=999;
    sent[N]=123; workspace[N]=123; backlog[N]=123; delays[N]=123; times[N]=123;
    CHECK(simulate_fifo_c(N,c,a,sent,backlog,delays,&completed,&remaining,times,workspace)==0);
    CHECK(sent[0]==0 && sent[1]==2 && sent[2]==1 && sent[3]==2);
    CHECK(backlog[0]==3 && backlog[1]==1 && backlog[2]==2 && backlog[3]==0);
    CHECK(completed==2 && delays[0]==2 && delays[1]==1 && remaining==0);
    CHECK(memcmp(c,original_c,sizeof c)==0 && memcmp(a,original_a,sizeof a)==0);
    CHECK(sent[N]==123 && workspace[N]==123 && backlog[N]==123 && delays[N]==123 && times[N]==123);
    CHECK(simulate_fifo_c(N,c,a,sent,backlog,delays,&completed,&remaining,times,workspace)==0);
    CHECK(completed==2 && remaining==0);
    uint32_t c2[N]={9,1,1,1}, a2[N]={5,1,0,0};
    CHECK(simulate_fifo_c(N,c2,a2,sent,backlog,delays,&completed,&remaining,times,workspace)==0);
    CHECK(completed==0 && remaining==3 && backlog[3]==3);
    CHECK(sent[0]==0 && sent[1]==1 && sent[2]==1 && sent[3]==1);
    uint32_t c3[N]={0,UINT32_MAX,0,0}, a3[N]={UINT32_MAX,UINT32_MAX,1,0};
    CHECK(simulate_fifo_c(N,c3,a3,sent,backlog,delays,&completed,&remaining,times,workspace)==0);
    CHECK(completed==1 && delays[0]==1 && remaining==(uint64_t)UINT32_MAX+1);
    CHECK(simulate_fifo_c(0,NULL,NULL,NULL,NULL,NULL,&completed,&remaining,NULL,NULL)==0);
    CHECK(completed==0 && remaining==0);
    CHECK(simulate_fifo_c(0,NULL,NULL,NULL,NULL,NULL,NULL,&remaining,NULL,NULL)==1);
    CHECK(simulate_fifo_c(N,NULL,a,sent,backlog,delays,&completed,&remaining,times,workspace)==1);
    CHECK(simulate_fifo_c(N,c,NULL,sent,backlog,delays,&completed,&remaining,times,workspace)==1);
    CHECK(simulate_fifo_c(N,c,a,NULL,backlog,delays,&completed,&remaining,times,workspace)==1);
    CHECK(simulate_fifo_c(N,c,a,sent,NULL,delays,&completed,&remaining,times,workspace)==1);
    CHECK(simulate_fifo_c(N,c,a,sent,backlog,NULL,&completed,&remaining,times,workspace)==1);
    CHECK(simulate_fifo_c(N,c,a,sent,backlog,delays,&completed,NULL,times,workspace)==1);
    CHECK(simulate_fifo_c(N,c,a,sent,backlog,delays,&completed,&remaining,NULL,workspace)==1);
    CHECK(simulate_fifo_c(N,c,a,sent,backlog,delays,&completed,&remaining,times,NULL)==1);
    uint32_t zeros[N]={0};
    CHECK(simulate_fifo_c(N,zeros,zeros,sent,backlog,delays,&completed,&remaining,times,workspace)==0);
    CHECK(completed==0 && remaining==0);
    for(size_t t=0;t<N;t++) CHECK(sent[t]==0 && backlog[t]==0);
    puts("All C FIFO acceptance checks passed.");
    return 0;
}
