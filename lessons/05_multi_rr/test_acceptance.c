#include "student.h"
#include <stdio.h>
#include <string.h>
#define CHECK(x) do {if(!(x)){fprintf(stderr,"FAIL line %d: %s\n",__LINE__,#x);return 1;}}while(0)
#define U 2
#define T 6
#define CALL(n,t,c,a) simulate_rr(n,t,c,a,selected,served,backlog,total,&completed,&remaining,times,left,head,tail,queued)
int main(void){
 uint32_t c[U*T]={2,1,2,1,2,1,2,1,2,1,2,1};
 uint32_t a[U*T]={1,1,1,0,0,1,0,0,0,0,0,0};
 uint32_t copyc[U*T],copya[U*T]; memcpy(copyc,c,sizeof c);memcpy(copya,a,sizeof a);
 size_t selected[T+1],times[U*T+1],head[U+1],tail[U+1],completed;
 uint32_t served[T+1],left[U*T+1];
 uint64_t backlog[U*T+1],total[U+1],queued[U+1],remaining;
 selected[T]=111;served[T]=111;times[U*T]=111;left[U*T]=111;
 backlog[U*T]=111;total[U]=111;queued[U]=111;head[U]=111;tail[U]=111;
 CHECK(CALL(U,4,c,a)==0);
 CHECK(selected[0]==RR_IDLE && selected[1]==0 && selected[2]==1 && selected[3]==0);
 CHECK(served[0]==0 && served[1]==1 && served[2]==1 && served[3]==1);
 uint64_t expected[]={1,1,1,1,1,1,0,1};
 CHECK(memcmp(backlog,expected,sizeof expected)==0);
 CHECK(total[0]==2 && total[1]==1 && completed==3 && remaining==1);
 CHECK(memcmp(c,copyc,sizeof c)==0 && memcmp(a,copya,sizeof a)==0);
 CHECK(CALL(U,T,c,a)==0);
 CHECK(selected[4]==1 && selected[5]==RR_IDLE && completed==4 && remaining==0);
 CHECK(selected[T]==111 && served[T]==111 && times[U*T]==111 && left[U*T]==111);
 CHECK(backlog[U*T]==111 && total[U]==111 && queued[U]==111 && head[U]==111 && tail[U]==111);
 /* 跳过容量为零的用户；未完成的大包仍按先进先出顺序优先发送。 */
 uint32_t cs[]={1,1,0,1,2,1,2,1,2,1};
 uint32_t as[]={5,1,1,0,0,0,0,0,0,0};
 CHECK(CALL(U,5,cs,as)==0);
 CHECK(selected[1]==1 && selected[2]==0 && selected[3]==0 && selected[4]==0);
 CHECK(completed==3 && remaining==0 && total[0]==6 && total[1]==1);
 /* 空闲时隙保持轮询起点：下次应选择符合服务条件的用户 1。 */
 uint32_t ci[]={1,1,1,1,0,0,1,1};
 uint32_t ai[]={1,1,1,0,0,0,0,0};
 CHECK(CALL(U,4,ci,ai)==0);
 CHECK(selected[2]==RR_IDLE && selected[3]==1);
 uint32_t zero[U*T]={0};
 CHECK(CALL(U,T,c,zero)==0);
 CHECK(completed==0 && remaining==0 && total[0]==0 && total[1]==0);
 for(size_t t=0;t<T;t++) CHECK(selected[t]==RR_IDLE && served[t]==0);
 for(size_t k=0;k<U*T;k++) CHECK(backlog[k]==0);
 uint32_t big[]={UINT32_MAX,UINT32_MAX,UINT32_MAX,UINT32_MAX};
 CHECK(CALL(U,2,zero,big)==0);
 CHECK(remaining==4*(uint64_t)UINT32_MAX && completed==0);
 CHECK(CALL(U,0,NULL,NULL)==0 && completed==0 && remaining==0);
 CHECK(CALL(0,0,NULL,NULL)==1);
 CHECK(CALL(SIZE_MAX,2,c,a)==2);
 CHECK(CALL(U,2,NULL,a)==1);
 CHECK(CALL(U,2,c,NULL)==1);
 CHECK(simulate_rr(U,2,c,a,NULL,served,backlog,total,&completed,&remaining,times,left,head,tail,queued)==1);
 CHECK(simulate_rr(U,2,c,a,selected,NULL,backlog,total,&completed,&remaining,times,left,head,tail,queued)==1);
 CHECK(simulate_rr(U,2,c,a,selected,served,NULL,total,&completed,&remaining,times,left,head,tail,queued)==1);
 CHECK(simulate_rr(U,2,c,a,selected,served,backlog,NULL,&completed,&remaining,times,left,head,tail,queued)==1);
 CHECK(simulate_rr(U,2,c,a,selected,served,backlog,total,NULL,&remaining,times,left,head,tail,queued)==1);
 CHECK(simulate_rr(U,2,c,a,selected,served,backlog,total,&completed,NULL,times,left,head,tail,queued)==1);
 CHECK(simulate_rr(U,2,c,a,selected,served,backlog,total,&completed,&remaining,NULL,left,head,tail,queued)==1);
 CHECK(simulate_rr(U,2,c,a,selected,served,backlog,total,&completed,&remaining,times,NULL,head,tail,queued)==1);
 CHECK(simulate_rr(U,2,c,a,selected,served,backlog,total,&completed,&remaining,times,left,NULL,tail,queued)==1);
 CHECK(simulate_rr(U,2,c,a,selected,served,backlog,total,&completed,&remaining,times,left,head,NULL,queued)==1);
 CHECK(simulate_rr(U,2,c,a,selected,served,backlog,total,&completed,&remaining,times,left,head,tail,NULL)==1);
 /* 逐段检查守恒：每用户累计到达量等于累计发送量加最终积压。 */
 for(size_t end=1;end<=T;end++){
  CHECK(CALL(U,end,c,a)==0);
  uint64_t sum_sent=0,sum_remaining=0;
  for(size_t u=0;u<U;u++){
   uint64_t arrived=0;for(size_t t=0;t<end;t++)arrived+=a[t*U+u];
   CHECK(arrived==total[u]+backlog[(end-1)*U+u]);
   sum_remaining+=backlog[(end-1)*U+u];
  }
  for(size_t t=0;t<end;t++){
   sum_sent+=served[t];
   CHECK(selected[t]==RR_IDLE || selected[t]<U);
   if(selected[t]==RR_IDLE) CHECK(served[t]==0);
   else CHECK(served[t]<=c[t*U+selected[t]]);
  }
  CHECK(sum_sent==total[0]+total[1] && sum_remaining==remaining);
 }
 /* 三用户：成功服务后起点为1；空闲搜索不可把起点改成0。 */
 {
  uint32_t cap[]={1,1,1, 1,1,1, 0,0,0, 1,1,1};
  uint32_t arr[]={1,1,1, 1,0,0, 0,0,0, 0,0,0};
  size_t sel[4],pt[12],h[3],tl[3],done;
  uint32_t sv[4],pl[12];uint64_t bg[12],tot[3],q[3],rem;
  CHECK(simulate_rr(3,4,cap,arr,sel,sv,bg,tot,&done,&rem,pt,pl,h,tl,q)==0);
  CHECK(sel[0]==RR_IDLE && sel[1]==0 && sel[2]==RR_IDLE && sel[3]==1);
 }
 /* 元素数可表示，但64位输出缓冲区所需字节数不可表示。 */
 CHECK(CALL(1,SIZE_MAX/sizeof(uint64_t)+1,c,a)==2);
 puts("All multi-user RR acceptance checks passed.");return 0;
}


