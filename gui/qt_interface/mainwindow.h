#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QLCDNumber>
#include <QLabel>
#include <QDoubleSpinBox>
#include <QPushButton>
#include "communication_client.h"

// Qt Charts includes
#include <QChartView>
#include <QLineSeries>
#include <QValueAxis>

/**
 * @brief Main window for Industrial Pressure Control System GUI
 * 
 * Displays three live plots (pressure, valve angle, motor current)
 * and a dashboard with controls and status indicators.
 */
class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    explicit MainWindow(QWidget *parent = nullptr);
    ~MainWindow();

public slots:
    /**
     * @brief Handle new data from simulation
     */
    void onDataUpdated(double pressure, double valveAngle, double motorCurrent,
                       double setpoint, double timestamp);

private slots:
    void onStartClicked();
    void onStopClicked();
    void onResetClicked();
    void onApplyGainsClicked();
    void onConnectionError(const QString& error);

private:
    void setupUI();
    void setupPlots();
    void setupDashboard();
    QChartView* createChart(const QString& title, const QString& yLabel,
                            QLineSeries* series, QLineSeries* referenceSeries = nullptr);

    // Communication
    CommunicationClient* m_client;

    // Chart views
    QChartView* m_pressureChartView;
    QChartView* m_valveChartView;
    QChartView* m_currentChartView;

    // Data series
    QLineSeries* m_pressureSeries;
    QLineSeries* m_setpointSeries;
    QLineSeries* m_valveAngleSeries;
    QLineSeries* m_motorCurrentSeries;

    // Dashboard widgets
    QLCDNumber* m_pressureLCD;
    QLabel* m_errorLabel;
    QLabel* m_statusLabel;
    QDoubleSpinBox* m_KpSpinBox;
    QDoubleSpinBox* m_KiSpinBox;
    QDoubleSpinBox* m_KdSpinBox;
    QPushButton* m_startButton;
    QPushButton* m_stopButton;
    QPushButton* m_resetButton;
    QPushButton* m_applyGainsButton;

    // Time window for scrolling plots (seconds)
    double m_timeWindow;
};

#endif // MAINWINDOW_H
