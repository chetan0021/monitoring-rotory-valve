/*
 * Main Window Header
 * 
 * Main GUI window for real-time system monitoring and control.
 * 
 * Features:
 * - Real-time pressure plot
 * - Valve angle display
 * - Motor current display
 * - Setpoint control
 * - System status indicators
 * 
 * References:
 * - docs/numerical_state_space_and_simulation_specification.md (Section 8)
 */

#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QTimer>
#include "communication_client.h"

class QCustomPlot;
class QLabel;
class QLineEdit;
class QPushButton;

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    explicit MainWindow(QWidget *parent = nullptr);
    ~MainWindow();

private slots:
    void updateDisplay();
    void onSetpointChanged();
    void onStartClicked();
    void onStopClicked();
    void onResetClicked();

private:
    void setupUI();
    void setupPlots();
    void setupControls();
    void setupStatusDisplay();

    // UI Components
    QCustomPlot *pressurePlot;
    QCustomPlot *currentPlot;
    QLabel *valveAngleLabel;
    QLabel *pressureLabel;
    QLabel *currentLabel;
    QLineEdit *setpointEdit;
    QPushButton *startButton;
    QPushButton *stopButton;
    QPushButton *resetButton;

    // Communication
    CommunicationClient *commClient;
    QTimer *updateTimer;

    // Data buffers for plotting
    QVector<double> timeData;
    QVector<double> pressureData;
    QVector<double> currentData;
};

#endif // MAINWINDOW_H
