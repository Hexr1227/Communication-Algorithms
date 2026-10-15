#include "student.h"
#include <math.h>
#include <stdio.h>
#include <string.h>
#define CHECK(x) do{if(!(x)){fprintf(stderr,"验收失败，行%d：%s\n",__LINE__,#x);return 1;}}while(0)
#define CALL(U,T,P,AL,C,A) simulate_policy(U,T,P,AL,C,A,sel,sv,bg,tot,&done,&rem,pt,pl,h,tl,q,av)
int main(void){
 uint32_t c[]={2,1,2,1,2,1,2,1},a[]={1,1,1,0,0,1,0,0};
 size_t sel[5],pt[9],h[3],tl[3],done;uint32_t sv[5],pl[9];
 uint64_t bg[9],tot[3],q[3],rem;double av[3];
 sel[4]=99;sv[4]=99;pt[8]=99;pl[8]=99;bg[8]=99;tot[2]=99;q[2]=99;h[2]=99;tl[2]=99;av[2]=99;
 CHECK(CALL(2,4,0,0.5,c,a)==0);
 CHECK(sel[0]==POLICY_IDLE&&sel[1]==0&&sel[2]==1&&sel[3]==0);
 CHECK(av[0]==0.6875&&av[1]==0.3125&&done==3&&rem==1);
 for(unsigned p=1;p<=3;p++){
  CHECK(CALL(2,4,p,0.5,c,a)==0);
  if(p==POLICY_PF){
   CHECK(sel[0]==POLICY_IDLE&&sel[1]==0&&sel[2]==1&&sel[3]==0);
   CHECK(av[0]==0.6875&&av[1]==0.3125&&rem==1);
  }else{
   CHECK(sel[0]==POLICY_IDLE&&sel[1]==0&&sel[2]==0&&sel[3]==1);
   CHECK(av[0]==0.4375&&av[1]==0.5625&&rem==1);
  }
 }
 CHECK(sel[4]==99&&sv[4]==99&&pt[8]==99&&pl[8]==99&&bg[8]==99&&tot[2]==99&&q[2]==99&&h[2]==99&&tl[2]==99&&av[2]==99);
 CHECK(CALL(2,4,4,0.5,c,a)==1);
 CHECK(CALL(2,4,0,NAN,c,a)==1);
 CHECK(CALL(2,4,0,INFINITY,c,a)==1);
 CHECK(CALL(2,4,0,0,c,a)==1);
 CHECK(CALL(0,4,0,0.5,c,a)==1);
 CHECK(CALL(SIZE_MAX,2,0,0.5,c,a)==2);
 CHECK(CALL(1,SIZE_MAX/sizeof(uint64_t)+1,0,0.5,c,a)==2);
 CHECK(CALL(2,4,0,0.5,NULL,a)==1);
 CHECK(CALL(2,4,0,0.5,c,NULL)==1);
 CHECK(simulate_policy(2,4,0,0.5,c,a,sel,sv,bg,tot,&done,&rem,pt,pl,h,tl,q,NULL)==1);
 CHECK(simulate_policy(2,0,0,0.5,NULL,NULL,NULL,NULL,NULL,NULL,&done,&rem,NULL,NULL,NULL,NULL,NULL,NULL)==0);
 CHECK(done==0&&rem==0);
 puts("C集成验收通过。");return 0;
}

