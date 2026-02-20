/*
 * Main GUI Entry Point
 * 
 * Qt-based real-time monitoring interface for industrial pressure control system.
 * 
 * References:
 * - docs/numerical_state_space_and_simulation_specification.md (Section 8)
 */

#include <QApplication>
#include "mainwindow.h"

int main(int argc, char *argv[])
{
    QApplication app(argc, argv);
    
    MainWindow window;
    window.setWindowTitle("Industrial Pressure Control System Monitor");
    window.resize(1200, 800);
    window.show();
    
    return app.exec();
}
