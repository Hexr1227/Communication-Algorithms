#include "student.h"

int simulate_rr(size_t users, size_t slots,
    const uint32_t *capacities, const uint32_t *arrivals,
    size_t *selected, uint32_t *served, uint64_t *backlog,
    uint64_t *total_served, size_t *completed, uint64_t *remaining,
    size_t *packet_time, uint32_t *packet_left,
    size_t *head, size_t *tail, uint64_t *queued) {
    //校验接口要求和整数运算边界。
    if (users == 0){
        return 1;
    }
    if (completed == NULL || remaining == NULL){
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
        users > SIZE_MAX / sizeof(uint64_t)) {
        return 2;
    }

    //初始化每用户状态及轮询搜索起点。
    for (size_t i = 0; i < users; i++){
        head[i] = tail[i] = queued[i] = 0;
    }
    size_t rr_start = 0;
    *completed = 0;
    *remaining = 0;
    for (size_t user = 0; user < users; user++){
        total_served[user] = 0;
    }

    //每时隙最多选择并服务一位符合条件的用户。
    //先进行轮询选择有效用户进行发送
    for (size_t slot = 0; slot < slots; slot++){
        size_t rr_cnt = 1;
        selected[slot] = rr_start;
        served[slot] = 0;
        while (capacities[users * slot + rr_start] == 0 || queued[rr_start] == 0){
            if (rr_cnt == users){
                selected[slot] = RR_IDLE;
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
        if (selected[slot] == RR_IDLE){
            served[slot] = 0;
        }else{
            selected[slot] = rr_start;
            uint32_t deducted = capacities[users * slot + rr_start] > queued[rr_start] ? 
                                (uint32_t)queued[rr_start] : capacities[users * slot + rr_start];
            queued[rr_start] -= deducted;
            while (head[rr_start] < tail[rr_start] && deducted > 0){
                if (packet_left[rr_start * slots + head[rr_start]] > deducted){
                    packet_left[rr_start * slots + head[rr_start]] -= deducted;
                    served[slot] += deducted;
                    deducted = 0;
                }else{
                    deducted -= packet_left[rr_start * slots + head[rr_start]];
                    served[slot] += packet_left[rr_start * slots + head[rr_start]];
                    packet_left[rr_start * slots + head[rr_start]] = 0;
                    *completed += 1;
                    head[rr_start]++;
                }
            }
        }
        *remaining -= served[slot];
        if (total_served[rr_start] > UINT64_MAX - served[slot]) {
            return 2;
        }
        total_served[rr_start] += served[slot];

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

        //预备轮询到下一处
        if (rr_start == users - 1){
            rr_start = 0;
        }else{
            rr_start++;
        }
    }

    return 0;
}


