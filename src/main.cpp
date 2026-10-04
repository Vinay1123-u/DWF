#include <QApplication>

#include "ui/LoginWindow.h"
#include "services/AuthenticationService.h"

int main(int argc, char* argv[])
{
    QApplication app(argc, argv);
    app.setApplicationName("Dictionary Word Finder");
    app.setApplicationVersion("1.0.0");

    AuthenticationService authService;
    LoginWindow loginWindow(authService);
    loginWindow.show();

    return QApplication::exec();
}
