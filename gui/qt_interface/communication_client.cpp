#include "communication_client.h"
#include <QJsonDocument>
#include <QJsonObject>
#include <QDebug>

CommunicationClient::CommunicationClient(QObject *parent)
    : QObject(parent)
    , m_pythonProcess(new QProcess(this))
{
    // Connect process signals
    connect(m_pythonProcess, &QProcess::readyReadStandardOutput,
            this, &CommunicationClient::onReadyRead);
    connect(m_pythonProcess, &QProcess::errorOccurred,
            this, &CommunicationClient::onProcessError);
}

CommunicationClient::~CommunicationClient()
{
    stop();
}

void CommunicationClient::start(const QString& scriptPath)
{
    if (m_pythonProcess->state() == QProcess::Running) {
        qWarning() << "Process already running";
        return;
    }

    // Try both "python" and "python3" for cross-platform compatibility
    QStringList pythonCandidates = {"python", "python3"};
    bool started = false;
    
    for (const QString& pyExec : pythonCandidates) {
        QStringList arguments;
        arguments << scriptPath;
        
        m_pythonProcess->start(pyExec, arguments);
        
        if (m_pythonProcess->waitForStarted(2000)) {
            qInfo() << "Python simulation started successfully with" << pyExec;
            started = true;
            break;
        }
        
        // Kill failed attempt before trying next
        m_pythonProcess->kill();
        m_pythonProcess->waitForFinished(500);
    }
    
    if (!started) {
        QString error = QString("Failed to start Python simulation.\n"
                               "Please ensure Python 3.9+ is installed and in your system PATH.\n"
                               "Error: %1").arg(m_pythonProcess->errorString());
        emit connectionError(error);
        qCritical() << error;
    }
}

void CommunicationClient::stop()
{
    if (m_pythonProcess->state() == QProcess::Running) {
        m_pythonProcess->kill();
        m_pythonProcess->waitForFinished(3000);
        qInfo() << "Python simulation stopped";
    }
}

void CommunicationClient::sendGains(double Kp, double Ki, double Kd)
{
    if (m_pythonProcess->state() != QProcess::Running) {
        qWarning() << "Cannot send gains: process not running";
        return;
    }

    // Build JSON object
    QJsonObject json;
    json["Kp"] = Kp;
    json["Ki"] = Ki;
    json["Kd"] = Kd;

    // Serialize to compact JSON
    QJsonDocument doc(json);
    QByteArray data = doc.toJson(QJsonDocument::Compact);
    data.append('\n');

    // Write to Python stdin
    m_pythonProcess->write(data);
    qDebug() << "Sent gains:" << data;
}

void CommunicationClient::onReadyRead()
{
    // Read all available lines from stdout
    while (m_pythonProcess->canReadLine()) {
        QByteArray line = m_pythonProcess->readLine().trimmed();
        
        if (line.isEmpty()) {
            continue;
        }

        // Parse JSON
        QJsonDocument doc = QJsonDocument::fromJson(line);
        
        if (doc.isNull() || !doc.isObject()) {
            qWarning() << "Invalid JSON received:" << line;
            continue;
        }

        QJsonObject obj = doc.object();

        // Extract fields
        if (obj.contains("pressure") && obj.contains("valve_angle") &&
            obj.contains("motor_current") && obj.contains("setpoint") &&
            obj.contains("timestamp")) {
            
            double pressure = obj["pressure"].toDouble();
            double valveAngle = obj["valve_angle"].toDouble();
            double motorCurrent = obj["motor_current"].toDouble();
            double setpoint = obj["setpoint"].toDouble();
            double timestamp = obj["timestamp"].toDouble();

            // Emit signal with data
            emit dataUpdated(pressure, valveAngle, motorCurrent, setpoint, timestamp);
        } else {
            qWarning() << "JSON missing required fields:" << line;
        }
    }
}

void CommunicationClient::onProcessError(QProcess::ProcessError error)
{
    QString errorMsg;
    
    switch (error) {
        case QProcess::FailedToStart:
            errorMsg = "Python not found. Please install Python 3.9+ and ensure it is in your system PATH.";
            break;
        case QProcess::Crashed:
            errorMsg = "Python process crashed";
            break;
        case QProcess::Timedout:
            errorMsg = "Python process timed out";
            break;
        case QProcess::WriteError:
            errorMsg = "Write error to Python process";
            break;
        case QProcess::ReadError:
            errorMsg = "Read error from Python process";
            break;
        default:
            errorMsg = "Unknown process error";
            break;
    }

    emit connectionError(errorMsg);
    qCritical() << "Process error:" << errorMsg;
}
