#pragma once

#include <QMainWindow>
#include <QLabel>
#include <QLineEdit>
#include <QPushButton>
#include <QVBoxLayout>
#include <QFormLayout>

#include "services/AuthenticationService.h"

class RegisterWindow : public QMainWindow
{
    Q_OBJECT
public:
    explicit RegisterWindow(AuthenticationService& authService, QWidget* parent = nullptr);

private slots:
    void handleRegister();
    void openLogin();

private:
    AuthenticationService& m_authService;
    QWidget* m_centralWidget;
    QVBoxLayout* m_mainLayout;
    QLabel* m_titleLabel;
    QLineEdit* m_usernameInput;
    QLineEdit* m_emailInput;
    QLineEdit* m_passwordInput;
    QLineEdit* m_confirmPasswordInput;
    QPushButton* m_registerButton;
    QLabel* m_errorLabel;
    QPushButton* m_loginButton;
};
