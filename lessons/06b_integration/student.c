#include "student.h"
#include <math.h>

int simulate_policy(size_t users, size_t slots, unsigned policy, double alpha,
    const uint32_t *capacities, const uint32_t *arrivals,
    size_t *selected, uint32_t *served, uint64_t *backlog,
    uint64_t *total_served, size_t *completed, uint64_t *remaining,
    size_t *packet_time, uint32_t *packet_left,
    size_t *head, size_t *tail, uint64_t *queued, double *average) {
//校验和队列设计，初始化状态。
    //校验接口要求和整数运算边界。
    if (users == 0){
        return 1;
    }
    if (completed == NULL || remaining == NULL){
        return 1;
    }
    if (policy > 3){
        return 1;
    }
    if (alpha <= 0 || alpha > 1 || ! isfinite(alpha)){
        return 1;
    }
    if (slots == 0){
        *completed = 0;
        *remaining = 0;
        return 0;
    }
    if (users > SIZE_MAX / slots){
        return 2;
    }
    if (capacities == NULL || arrivals == NULL || selected == NULL || served == NULL ||
        backlog == NULL || total_served == NULL ||packet_time == NULL || packet_left == NULL 
        || head == NULL || tail == NULL || queued == NULL){
            return 1;
        }

    if (average == NULL){
        return 1;       
    }

    size_t cells = users * slots;

    //检查各数组不溢出
    if (cells > SIZE_MAX / sizeof(uint64_t) ||
        cells > SIZE_MAX / sizeof(size_t) ||
        cells > SIZE_MAX / sizeof(uint32_t)) {
        return 2;
    }
    if (slots > SIZE_MAX / sizeof(size_t) ||
        slots > SIZE_MAX / sizeof(uint32_t)) {
        return 2;
    }
    if (users > SIZE_MAX / sizeof(size_t) ||
        users > SIZE_MAX / sizeof(uint32_t) ||
        users > SIZE_MAX / sizeof(uint64_t) ||
        users > SIZE_MAX / sizeof(double)){
        return 2;
    }

//按策略选择用户，共用发送与到达处理。
    //初始化每用户状态。
    for (size_t i = 0; i < users; i++){
        head[i] = tail[i] = queued[i] = 0;
    }
    for (size_t user = 0; user < users; user++){
        total_served[user] = 0;
        average[user] = 1;
    }
    *completed = 0;
    *remaining = 0;
    size_t rr_start = 0;
    int status = 0;

    //每时隙最多选择并服务一位符合条件的用户。
    //选择有效用户进行发送，然后接收新包
    for (size_t slot = 0; slot < slots; slot++){
        served[slot] = 0;
        //若为轮询，选择用户
        if (policy == POLICY_RR){
            size_t rr_cnt = 1;
            selected[slot] = rr_start;
            while (capacities[users * slot + rr_start] == 0 || queued[rr_start] == 0){
                if (rr_cnt == users){
                    selected[slot] = POLICY_IDLE;
                    break;
                }else{
                    if (rr_start == users - 1){
                        rr_start = 0;
                        rr_cnt++;
                    }else{
                        rr_start++;
                        rr_cnt++;
                    }
                }
            }
        }else{
        //若为Max_rate或PF或Max_weight，选择用户
            status = choose_user(users, policy, capacities + users * slot, queued, average, selected + slot);
            if (status != 0){
                return status;
            }
        }
        //进行发送
        if (selected[slot] == POLICY_IDLE){
            served[slot] = 0;
        }else{
            if (policy == POLICY_RR){
                selected[slot] = rr_start;
            }
            size_t chosen = selected[slot];
            uint32_t deducted = capacities[users * slot + chosen] > queued[chosen] ? 
                                (uint32_t)queued[chosen] : capacities[users * slot + chosen];
            queued[chosen] -= deducted;
            while (head[chosen] < tail[chosen] && deducted > 0){
                if (packet_left[chosen * slots + head[chosen]] > deducted){
                    packet_left[chosen * slots + head[chosen]] -= deducted;
                    served[slot] += deducted;
                    deducted = 0;
                }else{
                    deducted -= packet_left[chosen * slots + head[chosen]];
                    served[slot] += packet_left[chosen * slots + head[chosen]];
                    packet_left[chosen * slots + head[chosen]] = 0;
                    *completed += 1;
                    head[chosen]++;
                }
            }
            if (total_served[chosen] > UINT64_MAX - served[slot]) {
                return 2;
            }
            total_served[chosen] += served[slot];
        }
        *remaining -= served[slot];

        //更新平均值
        status = update_average(users, alpha, selected[slot], served[slot], average);
        if (status != 0){
            return status;
        }

        //处理接收
        for (size_t user = 0; user < users; user++){
            if (arrivals[slot * users + user] > 0){
                if (queued[user] > UINT64_MAX - arrivals[slot * users + user]) {
                    return 2;
                }
                packet_left[slots * user + tail[user]] = arrivals[slot * users + user];
                packet_time[slots * user + tail[user]] = slot;
                tail[user] += 1;
                queued[user] += arrivals[slot * users + user];
            }
            if (*remaining > UINT64_MAX - arrivals[slot * users + user]) {
                return 2;
            }
            backlog[slot * users + user] = queued[user];
            *remaining += arrivals[slot * users + user];
        }

        //若为轮询，预备轮询到下一处
        if (policy == POLICY_RR){
            if (rr_start == users - 1){
                rr_start = 0;
            }else{
                rr_start++;
        }
        }
    }    

    return 0;
}
