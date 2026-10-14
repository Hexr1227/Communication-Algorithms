#include "student.h"

int simulate_fifo_c(size_t slots,
    const uint32_t *capacities, const uint32_t *arrivals,
    uint32_t *served, uint64_t *backlog, size_t *delays,
    size_t *completed_count, uint64_t *remaining,
    size_t *scratch, uint32_t *scratch_remaining) {

    if (completed_count == NULL || remaining == NULL) {
        return 1;
    }

    if (slots == 0) {
        *completed_count = 0;
        *remaining = 0;
        return 0;
    }

    if (capacities == NULL || arrivals == NULL || served == NULL ||
        backlog == NULL || delays == NULL || scratch == NULL ||
        scratch_remaining == NULL) {
        return 1;
    }

    size_t head = 0;  //下一个待发送包
    size_t tail = 0;  //下一个新包要写入的位置
    uint64_t now_sum = 0;
    *completed_count = 0;

    for (size_t ti = 0; ti < slots; ++ti) {
        uint32_t capacity_left = capacities[ti];

        //先发送
        while (head < tail && capacity_left > 0) {
            uint32_t deducted = scratch_remaining[head] < capacity_left
                ? scratch_remaining[head] : capacity_left;

            scratch_remaining[head] -= deducted;
            capacity_left -= deducted;

            if (scratch_remaining[head] == 0) {
                delays[*completed_count] = ti - scratch[head];
                ++(*completed_count);
                ++head;
            }
        }

        served[ti] = capacities[ti] - capacity_left;
        now_sum -= served[ti];

        //再接收本时隙末到达的新包。
        if (arrivals[ti] != 0) {
            if (now_sum > UINT64_MAX - arrivals[ti]) {
                return 2;
            }
            scratch[tail] = ti;
            scratch_remaining[tail] = arrivals[ti];
            ++tail;
            now_sum += arrivals[ti];
        }

        backlog[ti] = now_sum;
    }

    *remaining = now_sum;
    return 0;
}