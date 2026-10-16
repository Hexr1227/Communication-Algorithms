/* 第九课A核心验收：固定小样例，不包含参考仿真算法。 */
#include "student.h"
#ifdef NDEBUG
#undef NDEBUG
#endif
#include <assert.h>
#include <stdio.h>

static void check(size_t users, size_t slots, unsigned policy,
                  const uint32_t *capacities, const uint32_t *arrivals,
                  size_t expected_count, const size_t *expected_delays,
                  const size_t *expected_users) {
    size_t selected[16], packet_time[32], head[4], tail[4];
    uint32_t served[16], packet_left[32];
    uint64_t backlog[32], total_served[4], queued[4], remaining;
    double average[4];
    size_t completed = 99, delays[32], delay_users[32];
    assert(users <= 4 && slots <= 16 && users * slots <= 32);
    for (size_t i = 0; i < 32; ++i) {
        delays[i] = SIZE_MAX;
        delay_users[i] = SIZE_MAX;
    }
    int status = simulate_policy_delays(users, slots, policy, 0.5,
        capacities, arrivals, selected, served, backlog, total_served,
        &completed, &remaining, packet_time, packet_left,
        head, tail, queued, average, delays, delay_users);
    assert(status == 0);
    assert(completed == expected_count);
    for (size_t i = 0; i < completed; ++i) {
        assert(delays[i] == expected_delays[i]);
        assert(delay_users[i] == expected_users[i]);
    }
    /* 未使用样本区域必须保持原值。 */
    for (size_t i = completed; i < 32; ++i) {
        assert(delays[i] == SIZE_MAX);
        assert(delay_users[i] == SIZE_MAX);
    }
    uint64_t received = 0, sent = 0;
    for (size_t i = 0; i < users * slots; ++i) received += arrivals[i];
    for (size_t i = 0; i < users; ++i) sent += total_served[i];
    assert(received == sent + remaining);
    if (slots > 0) {
        assert(simulate_policy_delays(users, slots, policy, 0.5,
            capacities, arrivals, selected, served, backlog, total_served,
            &completed, &remaining, packet_time, packet_left,
            head, tail, queued, average, NULL, delay_users) == 1);
        assert(simulate_policy_delays(users, slots, policy, 0.5,
            capacities, arrivals, selected, served, backlog, total_served,
            &completed, &remaining, packet_time, packet_left,
            head, tail, queued, average, delays, NULL) == 1);
    }
}

int main(void) {
    const uint32_t c1[] = {3,3,3,3}, a1[] = {2,4,0,0};
    const size_t d1[] = {1,2}, u1[] = {0,0};
    const uint32_t c2[] = {0,0,10}, a2[] = {2,3,0};
    const size_t d2[] = {2,1};
    const uint32_t c3[] = {2,1,2,1,2,1,2,1};
    const uint32_t a3[] = {1,1,1,0,0,1,0,0};
    const size_t dr[] = {1,2,2}, ur[] = {0,1,0};
    const size_t dm[] = {1,1,3}, um[] = {0,0,1};
    const uint32_t cz[] = {0,0}, az[] = {1,1};
    const uint32_t cp[] = {1,1}, ap[] = {3,0};
    const uint32_t cl[] = {10}, al[] = {2};
    for (unsigned policy = 0; policy < 4; ++policy) {
        check(1,4,policy,c1,a1,2,d1,u1);
        check(1,3,policy,c2,a2,2,d2,u1);
        check(2,4,policy,c3,a3,3,
              policy == 0 || policy == 2 ? dr : dm,
              policy == 0 || policy == 2 ? ur : um);
        check(1,2,policy,cz,az,0,NULL,NULL);
        check(1,2,policy,cp,ap,0,NULL,NULL);
        check(1,1,policy,cl,al,0,NULL,NULL);
    }
    size_t completed = 99;
    uint64_t remaining = 99;
    assert(simulate_policy_delays(1,0,0,0.5,NULL,NULL,NULL,NULL,NULL,
        NULL,&completed,&remaining,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL) == 0);
    assert(completed == 0 && remaining == 0);
    puts("C delay acceptance checks passed.");
    return 0;
}

