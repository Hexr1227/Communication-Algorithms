#include "student.h"
#include <math.h>

int choose_user(size_t users, unsigned policy, const uint32_t *capacity,
                const uint64_t *queued, const double *average, size_t *selected) {
    //输入校验、符合条件的用户评分与并列处理。
    if (users == 0){
        return 1;
    }
    if (capacity == NULL || queued == NULL || selected == NULL){
        return 1;
    }
    if (policy == POLICY_PF && average == NULL){
        return 1;
    }
    if (users > SIZE_MAX / sizeof(size_t) ||
        users > SIZE_MAX / sizeof(uint32_t) ||
        users > SIZE_MAX / sizeof(uint64_t) ||
        users > SIZE_MAX / sizeof(double)){
            return 2;
    }

    *selected = POLICY_IDLE;
    switch (policy){
        case POLICY_MAX_RATE:{
            uint32_t max_rate = 0;
            for (size_t user = 0; user < users; user++){
                if (capacity[user] == 0 || queued[user] == 0){
                    continue;
                }
                uint32_t cur_rate = capacity[user] > queued[user] ?
                                        (uint32_t)queued[user] : capacity[user];
                if (cur_rate > max_rate){
                    max_rate = cur_rate;
                    *selected = user;
                }
            }
            break;
        }

        case POLICY_PF:{
            double max_PF = 0;
            double cur_T = 0;
            double cur_PF = 0;
            for (size_t user = 0; user < users; user++){
                if (average[user] < 0 || ! isfinite(average[user])){
                    return 1;
                }
                if (capacity[user] == 0 || queued[user] == 0){
                    continue;
                }
                cur_T = average[user] < 1e-9 ? 1e-9 : average[user];
                cur_PF = capacity[user] / cur_T;
                if (cur_PF > max_PF){
                    max_PF = cur_PF;
                    *selected = user;
                }
            }
            break;
        }

        case POLICY_MAX_WEIGHT:{
            double max_weight = 0;
            double cur_weight = 0;
            double cur_c = 0;
            double cur_q = 0;
            for (size_t user = 0; user < users; user++){
                if (capacity[user] == 0 || queued[user] == 0){
                    continue;
                }
                cur_c = (double)capacity[user];
                cur_q = (double)queued[user];
                cur_weight = cur_c * cur_q;
                if (cur_weight > max_weight){
                    max_weight = cur_weight;
                    *selected = user;
                }
            }
            break;
        }
        
        default:{
            return 1;
        }
    }

    return 0;
}

int update_average(size_t users, double alpha, size_t serviced,
                   uint32_t served, double *average) {
    //完整校验后更新所有用户的历史服务平均值。
    if (users == 0){
        return 1;
    }
    if (alpha <= 0 || alpha > 1 || ! isfinite(alpha)){
        return 1;
    }
    if (serviced >= users && serviced != POLICY_IDLE){
        return 1;
    }
    if (served != 0  && serviced == POLICY_IDLE){
        return 1;
    }
    if (average == NULL){
        return 1;
    }
    if (users > SIZE_MAX / sizeof(double)){
        return 2;
    }
    size_t user = 0;
    double cur_T = 0;
    for (user = 0; user < users; user++){
        cur_T = average[user];
        if (cur_T < 0 || ! isfinite(cur_T)){
            return 1;
        }
    }

    for (user = 0; user < users; user++){
        cur_T = average[user];
        double next_T = cur_T * (1 - alpha);
        if (user == serviced){
            next_T += (double)served * alpha;
        }
        average[user] = next_T;
    }

    return 0;
}
