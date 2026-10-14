#include "student.h"
#include <math.h>
#include <stdio.h>
#include <string.h>
#define CHECK(x) do{if(!(x)){fprintf(stderr,"失败，行%d：%s\n",__LINE__,#x);return 1;}}while(0)
#define CLOSE(a,b) (fabs((a)-(b))<1e-10)
int main(void){
 uint32_t c[]={8,5,2};uint64_t q[]={10,3,4};double avg[]={8,2,0.5};size_t pick;
 CHECK(choose_user(3,POLICY_MAX_RATE,c,q,NULL,&pick)==0 && pick==0);
 CHECK(choose_user(3,POLICY_PF,c,q,avg,&pick)==0 && pick==2);
 CHECK(choose_user(3,POLICY_MAX_WEIGHT,c,q,NULL,&pick)==0 && pick==0);
 CHECK(update_average(3,0.2,2,2,avg)==0);
 CHECK(CLOSE(avg[0],6.4)&&CLOSE(avg[1],1.6)&&CLOSE(avg[2],0.8));
 CHECK(update_average(3,0.5,POLICY_IDLE,0,avg)==0);
 CHECK(CLOSE(avg[0],3.2)&&CLOSE(avg[1],0.8)&&CLOSE(avg[2],0.4));
 CHECK(update_average(3,1.0,1,3,avg)==0 && avg[0]==0 && avg[1]==3 && avg[2]==0);
 uint32_t ct[]={9,2,2};uint64_t qt[]={1,5,5};double at[]={1,1,1};
 CHECK(choose_user(3,POLICY_MAX_RATE,ct,qt,NULL,&pick)==0 && pick==1);
 CHECK(choose_user(3,POLICY_MAX_WEIGHT,ct,qt,NULL,&pick)==0 && pick==1);
 uint32_t cz[]={9,0,2};uint64_t qz[]={0,5,1};
 for(unsigned p=1;p<=3;p++)CHECK(choose_user(3,p,cz,qz,at,&pick)==0 && pick==2);
 uint64_t empty[]={0,0,0};
 for(unsigned p=1;p<=3;p++)CHECK(choose_user(3,p,c,empty,at,&pick)==0 && pick==POLICY_IDLE);
 double flooravg[]={0,0,0};
 CHECK(choose_user(3,POLICY_PF,c,q,flooravg,&pick)==0 && pick==0);
 /* 乘积超过64位，但浮点评分仍可比较。 */
 uint32_t hugec[]={UINT32_MAX,1};uint64_t hugeq[]={UINT64_MAX,UINT64_MAX};
 CHECK(choose_user(2,POLICY_MAX_WEIGHT,hugec,hugeq,NULL,&pick)==0 && pick==0);
 CHECK(choose_user(0,1,c,q,NULL,&pick)==1);
 CHECK(choose_user(3,0,c,q,NULL,&pick)==1);
 CHECK(choose_user(3,1,NULL,q,NULL,&pick)==1);
 CHECK(choose_user(3,1,c,NULL,NULL,&pick)==1);
 CHECK(choose_user(3,1,c,q,NULL,NULL)==1);
 CHECK(choose_user(3,2,c,q,NULL,&pick)==1);
 CHECK(choose_user(SIZE_MAX,1,c,q,NULL,&pick)==2);
 double bad[]={1,NAN,1};
 CHECK(choose_user(3,2,c,q,bad,&pick)==1);
 bad[1]=INFINITY;CHECK(choose_user(3,2,c,q,bad,&pick)==1);
 bad[1]=-1;CHECK(choose_user(3,2,c,q,bad,&pick)==1);
 double saved[3];memcpy(saved,at,sizeof at);
 CHECK(update_average(3,0,0,1,at)==1);
 CHECK(update_average(3,1.1,0,1,at)==1);
 CHECK(update_average(3,NAN,0,1,at)==1);
 CHECK(update_average(3,INFINITY,0,1,at)==1);
 CHECK(update_average(3,0.1,3,1,at)==1);
 CHECK(update_average(3,0.1,POLICY_IDLE,1,at)==1);
 CHECK(update_average(3,0.1,0,1,NULL)==1);
 CHECK(memcmp(saved,at,sizeof at)==0);
 double invalid[]={1,2,NAN},snapshot[3];memcpy(snapshot,invalid,sizeof invalid);
 CHECK(update_average(3,0.1,0,1,invalid)==1);
 CHECK(memcmp(snapshot,invalid,sizeof invalid)==0);
 uint32_t cc[3];uint64_t qq[3];double aa[3];
 memcpy(cc,c,sizeof c);memcpy(qq,q,sizeof q);memcpy(aa,at,sizeof at);
 CHECK(choose_user(3,2,c,q,at,&pick)==0);
 CHECK(memcmp(cc,c,sizeof c)==0 && memcmp(qq,q,sizeof q)==0 && memcmp(aa,at,sizeof at)==0);
 puts("策略模块验收全部通过。");return 0;
}
