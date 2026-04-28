#ifndef CLARKE_PARK_H
#define CLARKE_PARK_H

#include <math.h>

typedef struct {
    float Ia;
    float Ib;
    float Angle;
    float Id;
    float Iq;
} ClarkePark_Transform;

void ClarkePark_Update(ClarkePark_Transform *cp);

#endif