// frontend/src/types.ts
export interface VectaraResult {
    prediction_id: string
    input_1: string
    input_2: string
    output_score: number
    timestamp: Date
    processing_time_ms: number
    status: string
}

export interface GibberishResult {
    prediction_id: string
    input_text: string
    predicted_label: string;
    prob_clean: number;
    prob_mild_gibberish: number;
    prob_noise: number;
    prob_word_salad: number;
    timestamp: Date
    processing_time_ms: number
    status: string
}