#include <QApplication>
#include "mainwindow.h"

int main(int argc, char *argv[])
{
    QApplication app(argc, argv);
    
    app.setApplicationName("Industrial Pressure Control System");
    app.setOrganizationName("Etheral X");
    app.setStyle("Fusion");
    
    MainWindow window;
    window.setWindowTitle("Industrial Pressure Control System — Etheral X");
    window.resize(1400, 900);
    window.setMinimumSize(1100, 700);
    window.show();
    
    return app.exec();
}
