function fetchChartData() {
  fetch('/test/get_data/')
    .then(response => response.json())
    .then(data => {
      mainSeries.setData(data.map(item => ({
        time: item.time,
        open: item.open,
        high: item.high,
        low: item.low,
        close: item.close,
      })));
      // Set the data for the SMA20 Series
      sma05Series.setData(data.map(item => ({
        time: item.time,
        value: item.sma05,
      })));
      sma20Series.setData(data.map(item => ({
        time: item.time,
        value: item.sma20,
      })));
      sma60Series.setData(data.map(item => ({
        time: item.time,
        value: item.sma60,
      })));
      bbUp2Series.setData(data.map(item => ({
        time: item.time,
        value: item.bb_up_2,
      })));
      bbDown2Series.setData(data.map(item => ({
        time: item.time,
        value: item.bb_down_2,
      })));
      bbUp3Series.setData(data.map(item => ({
        time: item.time,
        value: item.bb_up_3,
      })));
      bbDown3Series.setData(data.map(item => ({
        time: item.time,
        value: item.bb_down_3,
      })));
    });
}

// Create the Lightweight Chart within the container element
const chart = LightweightCharts.createChart(document.getElementById('container'));

// add
chart.timeScale().applyOptions({
    timeVisible: true,
    secondsVisible: false,
});

// Create the Main Series (Candlesticks)
const mainSeries = chart.addCandlestickSeries();

// add
mainSeries.applyOptions({
    priceLineVisible: true,
    lastValueVisible: true
});

const sma05Series = chart.addLineSeries({
    color: '#B8860B',
    lineWidth: 2,
    lastValueVisible: false,
    priceLineVisible: false,
});

const sma20Series = chart.addLineSeries({
    color: '#0000FF',
    lineWidth: 2,
    lastValueVisible: false,
    priceLineVisible: false,
});

const sma60Series = chart.addLineSeries({
    color: '#FFD700',
    lineWidth: 2,
    lastValueVisible: false,
    priceLineVisible: false,
});

const bbUp2Series = chart.addLineSeries({
    color: '#FF00FF',
    lineWidth: 2,
    lastValueVisible: false,
    priceLineVisible: false,
});

const bbDown2Series = chart.addLineSeries({
    color: '#FF00FF',
    lineWidth: 2,
    lastValueVisible: false,
    priceLineVisible: false,
});

const bbUp3Series = chart.addLineSeries({
    color: '#C71585',
    lineWidth: 2,
    lastValueVisible: false,
    priceLineVisible: false,
});

const bbDown3Series = chart.addLineSeries({
    color: '#C71585',
    lineWidth: 2,
    lastValueVisible: false,
    priceLineVisible: false,
});

// Fetch chart data
fetchChartData();

// Adding a window resize event handler to resize the chart when
// the window size changes.
window.addEventListener("resize", () => {
  chart.resize(window.innerWidth, window.innerHeight);
});
