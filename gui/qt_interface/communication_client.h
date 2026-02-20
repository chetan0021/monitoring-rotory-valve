#ifndef COMMUNICATION_CLIENT_H
#define COMMUNICATION_CLIENT_H

#include <QObject>
#include <QProcess>
#include <QString>

/**
 * @brief Communication client for Python simulation subprocess
 * 
 * Launches Python simulation as child process and communicates via stdout/stdin.
 * Receives JSON data lines from Python and emits signals for GUI updates.
 */
class CommunicationClient : public QObject
{
    Q_OBJECT

public:
    explicit CommunicationClient(QObject *parent = nullptr);
    ~CommunicationClient();

    /**
     * @brief Start Python simulation subprocess
     * @param scriptPath Path to simulation_runner.py
     */
    void start(const QString& scriptPath);

    /**
     * @brief Stop Python simulation subprocess
     */
    void stop();

    /**
     * @brief Send updated PID gains to Python simulation
     * @param Kp Proportional gain
     * @param Ki Integral gain
     * @param Kd Derivative gain
     */
    void sendGains(double Kp, double Ki, double Kd);

signals:
    /**
     * @brief Emitted when new simulation data is received
     * @param pressure Current pressure (bar)
     * @param valveAngle Valve angle (degrees)
     * @param motorCurrent Motor current (A)
     * @param setpoint Pressure setpoint (bar)
     * @param timestamp Simulation time (s)
     */
    void dataUpdated(double pressure, double valveAngle, double motorCurrent, 
                     double setpoint, double timestamp);

    /**
     * @brief Emitted when connection error occurs
     * @param errorMessage Error description
     */
    void connectionError(const QString& errorMessage);

private slots:
    /**
     * @brief Handle data available from Python stdout
     */
    void onReadyRead();

    /**
     * @brief Handle process errors
     */
    void onProcessError(QProcess::ProcessError error);

private:
    QProcess* m_pythonProcess;
};

#endif // COMMUNICATION_CLIENT_H
