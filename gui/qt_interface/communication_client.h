/*
 * Communication Client Header
 * 
 * ZeroMQ client for receiving system state and sending commands.
 * 
 * References:
 * - docs/numerical_state_space_and_simulation_specification.md (Section 8)
 */

#ifndef COMMUNICATION_CLIENT_H
#define COMMUNICATION_CLIENT_H

#include <QObject>
#include <QThread>
#include <QString>

// Forward declarations for ZeroMQ
namespace zmq {
    class context_t;
    class socket_t;
}

struct SystemState {
    double timestamp;
    double pressure;
    double valve_angle;
    double motor_current;
    double motor_velocity;
    double control_voltage;
    double setpoint;
};

class CommunicationClient : public QObject
{
    Q_OBJECT

public:
    explicit CommunicationClient(QObject *parent = nullptr);
    ~CommunicationClient();

    void start();
    void stop();
    
    SystemState getLatestState() const;
    
    void sendSetpointCommand(double setpoint);
    void sendStartCommand();
    void sendStopCommand();
    void sendResetCommand();

signals:
    void stateReceived(const SystemState &state);
    void connectionStatusChanged(bool connected);

private slots:
    void receiveData();

private:
    void connectToServer();
    void disconnectFromServer();
    
    zmq::context_t *context;
    zmq::socket_t *subSocket;   // For receiving state updates
    zmq::socket_t *reqSocket;   // For sending commands
    
    QThread *receiveThread;
    bool running;
    
    SystemState latestState;
    
    QString serverAddress;
    int subPort;
    int reqPort;
};

#endif // COMMUNICATION_CLIENT_H
