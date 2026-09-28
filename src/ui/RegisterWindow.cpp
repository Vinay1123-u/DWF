#include "ui/RegisterWindow.h"
#include <QVBoxLayout>
#include <QWidget>
#include "ui/LoginWindow.h"
#include "ui/MainWindow.h"
RegisterWindow::RegisterWindow(AuthenticationService& authService, QWidget* parent)
    : QMainWindow(parent), m_authService(authService)
{
    setWindowTitle("Create Account");
    resize(420, 620);
    setMinimumSize(360, 520);

    m_centralWidget = new QWidget(this);
    setCentralWidget(m_centralWidget);

    m_mainLayout = new QVBoxLayout(m_centralWidget);
    m_mainLayout->setContentsMargins(30, 30, 30, 30);
    m_mainLayout->setSpacing(12);

    m_titleLabel = new QLabel("Create Account", this);
    m_titleLabel->setStyleSheet("font-size: 28px; font-weight: 700;");

    m_usernameInput = new QLineEdit(this);
    m_usernameInput->setPlaceholderText("Username");
    m_usernameInput->setStyleSheet("QLineEdit { border: 1px solid #d1d5db; border-radius: 10px; padding: 12px; } QLineEdit:focus { border: 2px solid #2563eb; }");

    m_emailInput = new QLineEdit(this);
    m_emailInput->setPlaceholderText("Email");
    m_emailInput->setStyleSheet(m_usernameInput->styleSheet());

    m_passwordInput = new QLineEdit(this);
    m_passwordInput->setPlaceholderText("Password");
    m_passwordInput->setEchoMode(QLineEdit::Password);
    m_passwordInput->setStyleSheet(m_usernameInput->styleSheet());

    m_confirmPasswordInput = new QLineEdit(this);
    m_confirmPasswordInput->setPlaceholderText("Confirm Password");
    m_confirmPasswordInput->setEchoMode(QLineEdit::Password);
    m_confirmPasswordInput->setStyleSheet(m_usernameInput->styleSheet());

    m_registerButton = new QPushButton("Create Account", this);
    m_registerButton->setStyleSheet(
        "QPushButton { background: #2563eb; color: white; border-radius: 10px; padding: 12px; font-weight: 700; }"
        "QPushButton:hover { background: #1d4ed8; }"
    );

    m_errorLabel = new QLabel(this);
    m_errorLabel->setWordWrap(true);
    m_errorLabel->setStyleSheet("color: #dc2626; min-height: 18px;");

    m_loginButton = new QPushButton("Already have an account? Login", this);
    m_loginButton->setFlat(true);
    m_loginButton->setStyleSheet("QPushButton { color: #2563eb; font-weight: 600; } ");

    m_mainLayout->addWidget(m_titleLabel);
    m_mainLayout->addWidget(m_usernameInput);
    m_mainLayout->addWidget(m_emailInput);
    m_mainLayout->addWidget(m_passwordInput);
    m_mainLayout->addWidget(m_confirmPasswordInput);
    m_mainLayout->addWidget(m_registerButton);
    m_mainLayout->addWidget(m_errorLabel);
    m_mainLayout->addWidget(m_loginButton, 0, Qt::AlignCenter);
    m_mainLayout->addStretch();

    connect(m_registerButton, &QPushButton::clicked, this, &RegisterWindow::handleRegister);
    connect(m_loginButton, &QPushButton::clicked, this, &RegisterWindow::openLogin);
}

void RegisterWindow::handleRegister()
{
    const QString username = m_usernameInput->text();
    const QString email = m_emailInput->text();
    const QString password = m_passwordInput->text();
    const QString confirmPassword = m_confirmPasswordInput->text();

    if (username.trimmed().isEmpty()) {
        m_errorLabel->setText("Username is required.");
        return;
    }
    if (email.trimmed().isEmpty()) {
        m_errorLabel->setText("Email is required.");
        return;
    }
    if (password.isEmpty()) {
        m_errorLabel->setText("Password is required.");
        return;
    }
    if (password != confirmPassword) {
        m_errorLabel->setText("Passwords do not match.");
        return;
    }

    QString errorMessage;
    if (!m_authService.registerUser(username, email, password, errorMessage)) {
        m_errorLabel->setText(errorMessage);
        return;
    }

    if (m_authService.loginUser(email, password, errorMessage)) {
        auto* mainWindow = new MainWindow(m_authService, this);
        mainWindow->show();
        hide();
    } else {
        auto* loginWindow = new LoginWindow(m_authService, this);
        loginWindow->show();
        hide();
    }
}

void RegisterWindow::openLogin()
{
    auto* loginWindow = new LoginWindow(m_authService, this);
    loginWindow->show();
    hide();
}
