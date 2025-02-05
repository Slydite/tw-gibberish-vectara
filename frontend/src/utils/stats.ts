// frontend\src\utils\stats.ts
import { VectaraResult, GibberishResult } from '@/types'

export const calculateStats = (data: VectaraResult[] | GibberishResult[]) => {
    const total = data.length
    const score = data[0] && 'output_score' in data[0]
        ? data.map(d => (d as VectaraResult).output_score)
        : data.map(d => (d as GibberishResult).prob_clean)

    return {
        total,
        average: score.reduce((a, b) => a + b, 0) / total,
        min: Math.min(...score),
        max: Math.max(...score)
    }
} 