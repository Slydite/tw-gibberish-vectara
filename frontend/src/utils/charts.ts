import ApexCharts from 'apexcharts'
import { VectaraResult, GibberishResult } from '@/types'

export const initializeCharts = () => {
    const baseChartOptions = {
        chart: {
            height: 350,
            background: 'transparent',
            foreColor: '#fff',
            animations: {
                enabled: true,
                easing: 'easeinout',
                dynamicAnimation: {
                    speed: 1000
                }
            }
        },
        theme: {
            mode: 'dark'
        },
        series: [{
            name: 'Value',
            data: []
        }]
    };

    const timeSeriesBase = {
        ...baseChartOptions,
        chart: {
            ...baseChartOptions.chart,
            type: 'line'
        },
        stroke: {
            curve: 'smooth',
            width: 3
        },
        xaxis: {
            type: 'datetime',
            title: {
                text: 'Time',
                style: {
                    color: '#fff'
                }
            }
        },
        yaxis: {
            title: {
                style: {
                    color: '#fff'
                }
            }, grid: {
                color: '#545b5e'
            }
        },
        title: {
            align: 'left',
            style: {
                color: '#fff'
            }
        }
    };

    const barChartBase = {
        ...baseChartOptions,
        chart: {
            ...baseChartOptions.chart,
            type: 'bar'
        },
        plotOptions: {
            bar: {
                horizontal: false,
                columnWidth: '55%',
                endingShape: 'rounded',
                distributed: true
            }
        },
        dataLabels: {
            enabled: true,
            style: {
                colors: ['#fff']
            }
        },
        title: {
            align: 'left',
            style: {
                color: '#fff'
            }
        },
        yaxis: {
            title: {
                text: 'Count',
                style: {
                    color: '#fff'
                }
            }
        }
    };

    return {

        timeSeries: {
            ...timeSeriesBase,
            title: { text: 'Vectara Scores Over Time' },
            yaxis: { ...timeSeriesBase.yaxis, title: { text: 'Score', style: { color: '#fff' } } }
        },
        distribution: {
            ...barChartBase,
            title: { text: 'Score Distribution' },
            xaxis: {
                categories: ['0-0.25', '0.25-0.5', '0.5-0.75', '0.75-1.0'],
                title: { text: 'Score Range', style: { color: '#fff' } }
            }
        },


        cleanProb: {
            ...timeSeriesBase,
            title: { text: 'Clean Probability Over Time' },
            yaxis: { ...timeSeriesBase.yaxis, title: { text: 'Probability', style: { color: '#fff' } } }
        },
        mildGibberish: {
            ...timeSeriesBase,
            title: { text: 'Mild Gibberish Probability Over Time' },
            yaxis: { ...timeSeriesBase.yaxis, title: { text: 'Probability', style: { color: '#fff' } } }
        },
        noise: {
            ...timeSeriesBase,
            title: { text: 'Noise Probability Over Time' },
            yaxis: { ...timeSeriesBase.yaxis, title: { text: 'Probability', style: { color: '#fff' } } }
        },
        wordSalad: {
            ...timeSeriesBase,
            title: { text: 'Word Salad Probability Over Time' },
            yaxis: { ...timeSeriesBase.yaxis, title: { text: 'Probability', style: { color: '#fff' } } }
        },
        labelDistribution: {
            ...barChartBase,
            chart: {
                ...barChartBase.chart,
                type: 'bar'
            },
            plotOptions: {
                ...barChartBase.plotOptions,
                bar: {
                    ...barChartBase.plotOptions.bar,
                    distributed: true
                }
            },
            title: {
                text: 'Predicted Label Distribution',
                style: { color: '#fff' }
            },
            xaxis: {
                categories: ['Clean', 'Mild Gibberish', 'Noise', 'Word Salad'],
                title: {
                    text: 'Predicted Label',
                    style: { color: '#fff' }
                }
            },
            colors: ['#2ecc71', '#f1c40f', '#e67e22', '#e74c3c']
        },

        processingTime: {
            ...timeSeriesBase,
            title: { text: 'Processing Time Over Time' },
            yaxis: { ...timeSeriesBase.yaxis, title: { text: 'Processing Time (ms)', style: { color: '#fff' } } }
        }
    };
};

function calculateDistribution(values: number[]) {
    if (!values || values.length === 0) {
        return {
            categories: ['0-0.25', '0.25-0.5', '0.5-0.75', '0.75-1.0'],
            values: [0, 0, 0, 0]
        };
    }

    return {
        categories: ['0-0.25', '0.25-0.5', '0.5-0.75', '0.75-1.0'],
        values: [
            values.filter(v => v < 0.25).length,
            values.filter(v => v >= 0.25 && v < 0.5).length,
            values.filter(v => v >= 0.5 && v < 0.75).length,
            values.filter(v => v >= 0.75).length
        ]
    };
}

function calculateLabelDistribution(data: GibberishResult[]) {
    const labels = ['Clean', 'Mild Gibberish', 'Noise', 'Word Salad'];
    const counts = labels.map(label =>
        data.filter(d => d.predicted_label.toLowerCase() === label.toLowerCase()).length
    );

    console.log('Label distribution data:', { labels, counts });
    return {
        categories: labels,
        values: counts
    };
}

export const updateCharts = (
    charts: {
        timeSeries: ApexCharts | null;
        distribution: ApexCharts | null;
        cleanProb: ApexCharts | null;
        mildGibberish: ApexCharts | null;
        noise: ApexCharts | null;
        wordSalad: ApexCharts | null;
        labelDistribution: ApexCharts | null;
        processingTime: ApexCharts | null;
    },
    data: VectaraResult[] | GibberishResult[],
    modelType: string
) => {
    if (!data || !Array.isArray(data) || data.length === 0) return;

    try {
        if (modelType === 'Vectara') {
            const vectaraData = data as VectaraResult[];

            // Update score time series
            if (charts.timeSeries) {
                const timeSeriesData = vectaraData.map(item => ({
                    x: new Date(item.timestamp).getTime(),
                    y: parseFloat(item.output_score.toFixed(4))
                }));
                charts.timeSeries.updateSeries([{
                    name: 'Score',
                    data: timeSeriesData
                }]);
            }


            if (charts.distribution) {
                const distributionData = calculateDistribution(vectaraData.map(d => d.output_score));
                charts.distribution.updateSeries([{
                    name: 'Count',
                    data: distributionData.values
                }]);
            }
        } else {
            const gibberishData = data as GibberishResult[];

            if (charts.cleanProb) {
                charts.cleanProb.updateSeries([{
                    name: 'Clean Probability',
                    data: gibberishData.map(item => ({
                        x: new Date(item.timestamp).getTime(),
                        y: parseFloat(item.prob_clean.toFixed(4))
                    }))
                }]);
            }

            if (charts.mildGibberish) {
                charts.mildGibberish.updateSeries([{
                    name: 'Mild Gibberish Probability',
                    data: gibberishData.map(item => ({
                        x: new Date(item.timestamp).getTime(),
                        y: parseFloat(item.prob_mild_gibberish.toFixed(4))
                    }))
                }]);
            }

            if (charts.noise) {
                charts.noise.updateSeries([{
                    name: 'Noise Probability',
                    data: gibberishData.map(item => ({
                        x: new Date(item.timestamp).getTime(),
                        y: parseFloat(item.prob_noise.toFixed(4))
                    }))
                }]);
            }

            if (charts.wordSalad) {
                charts.wordSalad.updateSeries([{
                    name: 'Word Salad Probability',
                    data: gibberishData.map(item => ({
                        x: new Date(item.timestamp).getTime(),
                        y: parseFloat(item.prob_word_salad.toFixed(4))
                    }))
                }]);
            }

            if (charts.labelDistribution) {
                const labelDist = calculateLabelDistribution(gibberishData);
                console.log('Updating label distribution with:', labelDist);
                charts.labelDistribution.updateSeries([{
                    name: 'Count',
                    data: labelDist.values
                }]);
            }
        }

        if (charts.processingTime) {
            charts.processingTime.updateSeries([{
                name: 'Processing Time',
                data: data.map(item => ({
                    x: new Date(item.timestamp).getTime(),
                    y: item.processing_time_ms
                }))
            }]);
        }
    } catch (error) {
        console.error('Error updating charts:', error);
    }
};