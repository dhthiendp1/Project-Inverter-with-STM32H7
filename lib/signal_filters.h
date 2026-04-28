#ifndef SIGNAL_FILTERS_H
#define SIGNAL_FILTERS_H

#include <stdint.h>

#define AVG_WINDOW_SIZE 32

typedef struct {
    // Low Pass Filter
    float alpha;
    float lpf_out_prev;
    
    // Moving Average Filter
    float buffer[AVG_WINDOW_SIZE];
    uint8_t index;
    float sum;
} Filter_Struct;

void Filter_Init(Filter_Struct *f, float alpha);
float Filter_Apply(Filter_Struct *f, float input);

#endif