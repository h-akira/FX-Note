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
      sma20Series.setData(data.map(item => ({
        time: item.time,
        value: item.sma20,
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
// const mainSeries = chart.addCandlestickSeries({
    // lastValueVisible: false
// });

mainSeries.applyOptions({
    priceLineVisible: false,
    lastValueVisible: false
});

const sma20Series = chart.addLineSeries({
    color: '#FF0000',
    lineWidth: 2,
});

// Fetch chart data
fetchChartData();

// Adding a window resize event handler to resize the chart when
// the window size changes.
window.addEventListener("resize", () => {
  chart.resize(window.innerWidth, window.innerHeight);
});
