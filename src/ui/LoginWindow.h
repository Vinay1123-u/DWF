#pragma once

#include <QMainWindow>
#include <QLabel>
#include <QLineEdit>
#include <QPushButton>
#include <QCheckBox>
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QFormLayout>

#include "services/AuthenticationService.h"

class LoginWindow : public QMainWindow
{
    Q_OBJECT
public:
    explicit LoginWindow(AuthenticationService& authService, QWidget* parent = nullptr);

private slots:
    void handleLogin();
    void togglePasswordVisibility(bool checked);
    void openRegister();

private:
    AuthenticationService& m_authService;
    QWidget* m_centralWidget;
    QVBoxLayout* m_mainLayout;
    QLabel* m_titleLabel;
    QLabel* m_subtitleLabel;
    QLineEdit* m_emailInput;
    QLineEdit* m_passwordInput;
    QCheckBox* m_showPasswordCheck;
    QPushButton* m_loginButton;
    QLabel* m_errorLabel;
    QLabel* m_registerPrompt;
    QPushButton* m_createAccountButton;
};
