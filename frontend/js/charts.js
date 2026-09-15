// Chart.js Golden Visualizations

let revenueChartInstance = null;

function renderRevenueChart(chartData) {
  const ctx = document.getElementById("revenueChart");
  if (!ctx) return;

  if (revenueChartInstance) {
    revenueChartInstance.destroy();
  }

  const chartCtx = ctx.getContext("2d");

  // Create Golden Gradient
  const goldGradient = chartCtx.createLinearGradient(0, 0, 0, 300);
  goldGradient.addColorStop(0, "rgba(229, 193, 88, 0.85)");
  goldGradient.addColorStop(1, "rgba(197, 155, 39, 0.2)");

  const bronzeGradient = chartCtx.createLinearGradient(0, 0, 0, 300);
  bronzeGradient.addColorStop(0, "rgba(180, 130, 40, 0.8)");
  bronzeGradient.addColorStop(1, "rgba(120, 80, 20, 0.15)");

  revenueChartInstance = new Chart(ctx, {
    type: "bar",
    data: {
      labels: chartData.labels,
      datasets: [
        {
          label: "Gross Revenue ($)",
          data: chartData.revenue,
          backgroundColor: goldGradient,
          borderColor: "#D4AF37",
          borderWidth: 2,
          borderRadius: 8,
          borderSkipped: false
        },
        {
          label: "Net Operating Profit ($)",
          data: chartData.profit,
          backgroundColor: bronzeGradient,
          borderColor: "#9A771C",
          borderWidth: 2,
          borderRadius: 8,
          borderSkipped: false
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: "top",
          labels: {
            font: { family: "Outfit", size: 13, weight: "600" },
            color: "#1A1A1A",
            usePointStyle: true,
            boxWidth: 10
          }
        },
        tooltip: {
          backgroundColor: "#FFFFFF",
          titleColor: "#1A1A1A",
          bodyColor: "#D4AF37",
          borderColor: "rgba(212, 175, 55, 0.4)",
          borderWidth: 1,
          padding: 12,
          displayColors: true,
          boxPadding: 6,
          titleFont: { family: "Outfit", weight: "700" },
          bodyFont: { family: "Outfit", weight: "600" },
          callbacks: {
            label: function(context) {
              return ` ${context.dataset.label}: $${context.raw.toLocaleString()}`;
            }
          }
        }
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: { font: { family: "Outfit", size: 12 }, color: "#666666" }
        },
        y: {
          grid: { color: "rgba(212, 175, 55, 0.1)" },
          ticks: {
            font: { family: "Outfit", size: 12 },
            color: "#666666",
            callback: function(val) { return "$" + val.toLocaleString(); }
          }
        }
      }
    }
  });
}
