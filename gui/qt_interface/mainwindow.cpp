#include "mainwindow.h"
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QGroupBox>
#include <QChart>
#include <QPen>
#include <QTimer>
#include <QCoreApplication>
#include <QDir>
#include <QFile>
#include <QMessageBox>
#include <cmath>

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
    , m_client(new CommunicationClient(this))
    , m_timeWindow(15.0)
{
    setupUI();
    
    // Connect client signals
    connect(m_client, &CommunicationClient::dataUpdated,
            this, &MainWindow::onDataUpdated);
    connect(m_client, &CommunicationClient::connectionError,
            this, &MainWindow::onConnectionError);
}

MainWindow::~MainWindow()
{
}

void MainWindow::setupUI()
{
    // Create central widget
    QWidget* centralWidget = new QWidget(this);
    setCentralWidget(centralWidget);
    
    // Main horizontal layout
    QHBoxLayout* mainLayout = new QHBoxLayout(centralWidget);
    
    // Left side: plots (70% width)
    QWidget* plotsWidget = new QWidget();
    QVBoxLayout* plotsLayout = new QVBoxLayout(plotsWidget);
    plotsLayout->setContentsMargins(5, 5, 5, 5);
    plotsLayout->setSpacing(10);
    
    setupPlots();
    plotsLayout->addWidget(m_pressureChartView);
    plotsLayout->addWidget(m_valveChartView);
    plotsLayout->addWidget(m_currentChartView);
    
    // Right side: dashboard (30% width)
    setupDashboard();
    
    // Add to main layout
    mainLayout->addWidget(plotsWidget, 7);
}

void MainWindow::setupPlots()
{
    // Create series
    m_pressureSeries = new QLineSeries();
    m_setpointSeries = new QLineSeries();
    m_valveAngleSeries = new QLineSeries();
    m_motorCurrentSeries = new QLineSeries();
    
    // Style series
    QPen pressurePen(QColor(0, 120, 215), 2);  // Blue
    m_pressureSeries->setPen(pressurePen);
    
    QPen setpointPen(QColor(220, 50, 50), 1, Qt::DashLine);  // Red dashed
    m_setpointSeries->setPen(setpointPen);
    
    QPen valvePen(QColor(50, 180, 50), 2);  // Green
    m_valveAngleSeries->setPen(valvePen);
    
    QPen currentPen(QColor(255, 140, 0), 2);  // Orange
    m_motorCurrentSeries->setPen(currentPen);
    
    // Create chart views
    m_pressureChartView = createChart("Tube Pressure (bar)", "Pressure (bar)",
                                      m_pressureSeries, m_setpointSeries);
    m_valveChartView = createChart("Valve Angle (degrees)", "Angle (°)",
                                   m_valveAngleSeries);
    m_currentChartView = createChart("Motor Current (A)", "Current (A)",
                                     m_motorCurrentSeries);
}

QChartView* MainWindow::createChart(const QString& title, const QString& yLabel,
                                    QLineSeries* series, QLineSeries* referenceSeries)
{
    QChart* chart = new QChart();
    chart->setTitle(title);
    chart->addSeries(series);
    
    if (referenceSeries) {
        chart->addSeries(referenceSeries);
    }
    
    // Create axes
    QValueAxis* axisX = new QValueAxis();
    axisX->setTitleText("Time (s)");
    axisX->setLabelFormat("%.1f");
    axisX->setRange(0, m_timeWindow);
    axisX->setGridLineVisible(true);
    
    QValueAxis* axisY = new QValueAxis();
    axisY->setTitleText(yLabel);
    axisY->setLabelFormat("%.1f");
    axisY->setGridLineVisible(true);
    
    // Set Y range based on chart type
    if (title.contains("Pressure")) {
        axisY->setRange(0, 700);
    } else if (title.contains("Valve")) {
        axisY->setRange(0, 180);
    } else {
        axisY->setRange(0, 25);  // Motor current
    }
    
    chart->addAxis(axisX, Qt::AlignBottom);
    chart->addAxis(axisY, Qt::AlignLeft);
    
    series->attachAxis(axisX);
    series->attachAxis(axisY);
    
    if (referenceSeries) {
        referenceSeries->attachAxis(axisX);
        referenceSeries->attachAxis(axisY);
    }
    
    chart->legend()->setVisible(false);
    
    QChartView* chartView = new QChartView(chart);
    chartView->setRenderHint(QPainter::Antialiasing);
    
    return chartView;
}

void MainWindow::setupDashboard()
{
    QWidget* dashboard = new QWidget();
    dashboard->setMaximumWidth(400);
    dashboard->setMinimumWidth(300);
    
    QVBoxLayout* layout = new QVBoxLayout(dashboard);
    layout->setContentsMargins(10, 10, 10, 10);
    layout->setSpacing(15);
    
    // Title
    QLabel* titleLabel = new QLabel("PRESSURE MONITOR");
    QFont titleFont = titleLabel->font();
    titleFont.setPointSize(14);
    titleFont.setBold(true);
    titleLabel->setFont(titleFont);
    titleLabel->setAlignment(Qt::AlignCenter);
    layout->addWidget(titleLabel);
    
    // Separator
    QFrame* line1 = new QFrame();
    line1->setFrameShape(QFrame::HLine);
    line1->setFrameShadow(QFrame::Sunken);
    layout->addWidget(line1);
    
    // Current pressure display
    QLabel* pressureLabel = new QLabel("Current Pressure");
    pressureLabel->setAlignment(Qt::AlignCenter);
    layout->addWidget(pressureLabel);
    
    m_pressureLCD = new QLCDNumber();
    m_pressureLCD->setDigitCount(6);
    m_pressureLCD->setSegmentStyle(QLCDNumber::Flat);
    m_pressureLCD->setMinimumHeight(60);
    layout->addWidget(m_pressureLCD);
    
    QLabel* barLabel = new QLabel("bar");
    barLabel->setAlignment(Qt::AlignCenter);
    layout->addWidget(barLabel);
    
    // Setpoint and error
    QLabel* setpointLabel = new QLabel("Setpoint: 500 bar");
    setpointLabel->setAlignment(Qt::AlignCenter);
    layout->addWidget(setpointLabel);
    
    m_errorLabel = new QLabel("Error: 0.00 bar");
    m_errorLabel->setAlignment(Qt::AlignCenter);
    layout->addWidget(m_errorLabel);
    
    m_statusLabel = new QLabel("● STABLE");
    m_statusLabel->setAlignment(Qt::AlignCenter);
    QFont statusFont = m_statusLabel->font();
    statusFont.setPointSize(12);
    statusFont.setBold(true);
    m_statusLabel->setFont(statusFont);
    m_statusLabel->setStyleSheet("color: green;");
    layout->addWidget(m_statusLabel);
    
    // Separator
    QFrame* line2 = new QFrame();
    line2->setFrameShape(QFrame::HLine);
    line2->setFrameShadow(QFrame::Sunken);
    layout->addWidget(line2);
    
    // PID gains
    QLabel* gainsLabel = new QLabel("PID Controller Gains");
    QFont gainsFont = gainsLabel->font();
    gainsFont.setBold(true);
    gainsLabel->setFont(gainsFont);
    layout->addWidget(gainsLabel);
    
    // Kp
    QHBoxLayout* kpLayout = new QHBoxLayout();
    kpLayout->addWidget(new QLabel("Kp:"));
    m_KpSpinBox = new QDoubleSpinBox();
    m_KpSpinBox->setRange(0, 1000);
    m_KpSpinBox->setValue(115.2);
    m_KpSpinBox->setSingleStep(0.1);
    m_KpSpinBox->setDecimals(1);
    kpLayout->addWidget(m_KpSpinBox);
    layout->addLayout(kpLayout);
    
    // Ki
    QHBoxLayout* kiLayout = new QHBoxLayout();
    kiLayout->addWidget(new QLabel("Ki:"));
    m_KiSpinBox = new QDoubleSpinBox();
    m_KiSpinBox->setRange(0, 1000);
    m_KiSpinBox->setValue(34.56);
    m_KiSpinBox->setSingleStep(0.1);
    m_KiSpinBox->setDecimals(2);
    kiLayout->addWidget(m_KiSpinBox);
    layout->addLayout(kiLayout);
    
    // Kd
    QHBoxLayout* kdLayout = new QHBoxLayout();
    kdLayout->addWidget(new QLabel("Kd:"));
    m_KdSpinBox = new QDoubleSpinBox();
    m_KdSpinBox->setRange(0, 1000);
    m_KdSpinBox->setValue(49.92);
    m_KdSpinBox->setSingleStep(0.1);
    m_KdSpinBox->setDecimals(2);
    kdLayout->addWidget(m_KdSpinBox);
    layout->addLayout(kdLayout);
    
    m_applyGainsButton = new QPushButton("Apply Gains");
    m_applyGainsButton->setStyleSheet("background-color: #808080; color: white;");
    connect(m_applyGainsButton, &QPushButton::clicked,
            this, &MainWindow::onApplyGainsClicked);
    layout->addWidget(m_applyGainsButton);
    
    // Separator
    QFrame* line3 = new QFrame();
    line3->setFrameShape(QFrame::HLine);
    line3->setFrameShadow(QFrame::Sunken);
    layout->addWidget(line3);
    
    // Control buttons
    m_startButton = new QPushButton("▶ Start Simulation");
    m_startButton->setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;");
    m_startButton->setMinimumHeight(40);
    connect(m_startButton, &QPushButton::clicked,
            this, &MainWindow::onStartClicked);
    layout->addWidget(m_startButton);
    
    m_stopButton = new QPushButton("■ Stop");
    m_stopButton->setStyleSheet("background-color: #f44336; color: white; font-weight: bold;");
    m_stopButton->setMinimumHeight(40);
    m_stopButton->setEnabled(false);
    connect(m_stopButton, &QPushButton::clicked,
            this, &MainWindow::onStopClicked);
    layout->addWidget(m_stopButton);
    
    m_resetButton = new QPushButton("↺ Reset");
    m_resetButton->setStyleSheet("background-color: #808080; color: white; font-weight: bold;");
    m_resetButton->setMinimumHeight(40);
    m_resetButton->setEnabled(false);
    connect(m_resetButton, &QPushButton::clicked,
            this, &MainWindow::onResetClicked);
    layout->addWidget(m_resetButton);
    
    // Separator
    QFrame* line4 = new QFrame();
    line4->setFrameShape(QFrame::HLine);
    line4->setFrameShadow(QFrame::Sunken);
    layout->addWidget(line4);
    
    // Footer
    QLabel* footerLabel1 = new QLabel("Industrial Pressure Control System");
    footerLabel1->setAlignment(Qt::AlignCenter);
    QFont footerFont = footerLabel1->font();
    footerFont.setPointSize(8);
    footerLabel1->setFont(footerFont);
    layout->addWidget(footerLabel1);
    
    QLabel* footerLabel2 = new QLabel("Etheral X — Assignment II");
    footerLabel2->setAlignment(Qt::AlignCenter);
    footerLabel2->setFont(footerFont);
    layout->addWidget(footerLabel2);
    
    layout->addStretch();
    
    // Add dashboard to main layout (30% width)
    QHBoxLayout* mainLayout = qobject_cast<QHBoxLayout*>(centralWidget()->layout());
    if (mainLayout) {
        mainLayout->addWidget(dashboard, 3);
    }
}

void MainWindow::onDataUpdated(double pressure, double valveAngle, double motorCurrent,
                               double setpoint, double timestamp)
{
    // Append new data points
    m_pressureSeries->append(timestamp, pressure);
    m_valveAngleSeries->append(timestamp, valveAngle);
    m_motorCurrentSeries->append(timestamp, motorCurrent);
    
    // Remove old points outside time window
    while (!m_pressureSeries->points().isEmpty() &&
           m_pressureSeries->points().first().x() < timestamp - m_timeWindow) {
        m_pressureSeries->remove(0);
    }
    while (!m_valveAngleSeries->points().isEmpty() &&
           m_valveAngleSeries->points().first().x() < timestamp - m_timeWindow) {
        m_valveAngleSeries->remove(0);
    }
    while (!m_motorCurrentSeries->points().isEmpty() &&
           m_motorCurrentSeries->points().first().x() < timestamp - m_timeWindow) {
        m_motorCurrentSeries->remove(0);
    }
    
    // Update setpoint reference line (horizontal line at 500 bar)
    m_setpointSeries->clear();
    double tStart = std::max(0.0, timestamp - m_timeWindow);
    m_setpointSeries->append(tStart, 500.0);
    m_setpointSeries->append(timestamp, 500.0);
    
    // Update X axes to scroll
    QChart* pressureChart = m_pressureChartView->chart();
    QChart* valveChart = m_valveChartView->chart();
    QChart* currentChart = m_currentChartView->chart();
    
    if (timestamp > m_timeWindow) {
        pressureChart->axes(Qt::Horizontal).first()->setRange(timestamp - m_timeWindow, timestamp);
        valveChart->axes(Qt::Horizontal).first()->setRange(timestamp - m_timeWindow, timestamp);
        currentChart->axes(Qt::Horizontal).first()->setRange(timestamp - m_timeWindow, timestamp);
    }
    
    // Update dashboard
    m_pressureLCD->display(pressure);
    
    double error = 500.0 - pressure;
    m_errorLabel->setText(QString("Error: %1 bar").arg(error, 0, 'f', 2));
    
    // Update status (5% of 500 = 25 bar tolerance)
    if (std::abs(error) <= 25.0) {
        m_statusLabel->setText("● STABLE");
        m_statusLabel->setStyleSheet("color: green; font-weight: bold;");
    } else {
        m_statusLabel->setText("● WARNING");
        m_statusLabel->setStyleSheet("color: red; font-weight: bold;");
    }
}

void MainWindow::onStartClicked()
{
    // Construct absolute path to simulation_runner.py
    // Qt executable is in gui/build/Release/ (Windows) or gui/build/ (Unix)
    // simulation_runner.py is in project root
    QString appDir = QCoreApplication::applicationDirPath();
    QDir projectRoot(appDir);
    
    // Navigate from build folder up to project root
    // Check if we're in a Release/Debug subfolder
    if (projectRoot.dirName() == "Release" || projectRoot.dirName() == "Debug") {
        projectRoot.cdUp();  // From Release/ to build/
    }
    projectRoot.cdUp();  // From build/ to gui/
    projectRoot.cdUp();  // From gui/ to project root
    
    QString scriptPath = projectRoot.absoluteFilePath("simulation_runner.py");
    
    // Verify the file exists before launching
    if (!QFile::exists(scriptPath)) {
        QMessageBox::critical(this, "Error",
            QString("Cannot find simulation_runner.py at:\n%1\n\n"
                   "Please ensure the project structure is intact.").arg(scriptPath));
        return;
    }
    
    m_client->start(scriptPath);
    
    // Update button states
    m_startButton->setEnabled(false);
    m_stopButton->setEnabled(true);
    m_resetButton->setEnabled(true);
}

void MainWindow::onStopClicked()
{
    m_client->stop();
    
    // Update button states
    m_startButton->setEnabled(true);
    m_stopButton->setEnabled(false);
    m_resetButton->setEnabled(false);
}

void MainWindow::onResetClicked()
{
    // Stop simulation
    m_client->stop();
    
    // Clear all series
    m_pressureSeries->clear();
    m_setpointSeries->clear();
    m_valveAngleSeries->clear();
    m_motorCurrentSeries->clear();
    
    // Reset X-axis ranges to initial state
    QChart* pressureChart = m_pressureChartView->chart();
    QChart* valveChart = m_valveChartView->chart();
    QChart* currentChart = m_currentChartView->chart();
    
    pressureChart->axes(Qt::Horizontal).first()->setRange(0, m_timeWindow);
    valveChart->axes(Qt::Horizontal).first()->setRange(0, m_timeWindow);
    currentChart->axes(Qt::Horizontal).first()->setRange(0, m_timeWindow);
    
    // Reset LCD and labels to initial state
    m_pressureLCD->display(0);
    m_errorLabel->setText("Error: 0.00 bar");
    m_statusLabel->setText("● STABLE");
    m_statusLabel->setStyleSheet("color: green; font-weight: bold;");
    
    // Restart after 500ms delay
    QTimer::singleShot(500, this, &MainWindow::onStartClicked);
}

void MainWindow::onApplyGainsClicked()
{
    double Kp = m_KpSpinBox->value();
    double Ki = m_KiSpinBox->value();
    double Kd = m_KdSpinBox->value();
    
    m_client->sendGains(Kp, Ki, Kd);
}

void MainWindow::onConnectionError(const QString& error)
{
    QMessageBox::critical(this, "Connection Error", error);
    
    // Reset button states
    m_startButton->setEnabled(true);
    m_stopButton->setEnabled(false);
    m_resetButton->setEnabled(false);
}
