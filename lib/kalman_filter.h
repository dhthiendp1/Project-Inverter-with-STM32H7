#ifndef KALMAN_FILTER_H
#define KALMAN_FILTER_H

typedef struct {
    float x;        /* Giá trị ước lượng (đầu ra bộ lọc) */
    float p;        /* Sai số ước lượng (Error covariance) */
    float q;        /* Nhiễu hệ thống (Process noise) */
    float r;        /* Nhiễu đo lường (Measurement noise) */
    float k;        /* Hệ số Kalman (Kalman gain) */
} Kalman_Struct;

void Kalman_Init(Kalman_Struct *kf, float q, float r);

float Kalman_Update(Kalman_Struct *kf, float measurement);

#endif