#ifndef PI_2P2Z_H
#define PI_2P2Z_H

typedef struct {
    float coeff_b2;
    float coeff_b1;
    float coeff_b0;
    float coeff_a2;
    float coeff_a1;
    
    float max;     // Giới hạn trên của đầu ra
    float i_min;   // Giới hạn dưới cho giá trị lịch sử (tránh wind-up)
    float min;     // Giới hạn dưới của đầu ra
} PI_2P2Z_COEFFS;

typedef struct {
    // Biến lịch sử đầu ra u(n-1), u(n-2)
    float out1;
    float out2;
    
    // Biến lịch sử sai số e(n), e(n-1), e(n-2)
    float errn;
    float errn1;
    float errn2;
    
    // Tín hiệu đầu vào
    float ref;     // et point
    float fdbk;    // Feedback
    
    float out;
} PI_2P2Z_VARS;

// Khai báo nguyên mẫu hàm
void PI_2P2Z_Init(PI_2P2Z_VARS *vars);
void PI_2P2Z_Update(PI_2P2Z_COEFFS *coeffs, PI_2P2Z_VARS *vars);

#endif // PI_2P2Z_H