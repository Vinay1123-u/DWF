#include "ui/LoginWindow.h"

#include <QApplication>
#include <QMessageBox>
#include <QPalette>
#include <QPixmap>
#include <QStyle>
#include <QVBoxLayout>
#include <QWidget>

#include "ui/RegisterWindow.h"
#include "ui/MainWindow.h"

LoginWindow::LoginWindow(AuthenticationService& authService, QWidget* parent)
    : QMainWindow(parent), m_authService(authService)
{
    setWindowTitle("Dictionary Word Finder — Sign In");
    resize(460, 620);
    setMinimumSize(400, 560);
    setWindowFlag(Qt::WindowContextHelpButtonHint, false);

    m_centralWidget = new QWidget(this);
    setCentralWidget(m_centralWidget);

    m_mainLayout = new QVBoxLayout(m_centralWidget);
    m_mainLayout->setContentsMargins(40, 44, 40, 40);
    m_mainLayout->setSpacing(16);

    m_titleLabel = new QLabel("Dictionary Word Finder", this);
    m_titleLabel->setStyleSheet(
        "font-size: 26px; font-weight: 800; color: #1e293b; letter-spacing: -0.5px;"
    );

    m_subtitleLabel = new QLabel("Welcome back! Please sign in to continue.", this);
    m_subtitleLabel->setStyleSheet(
        "font-size: 14px; font-weight: 500; color: #64748b; margin-bottom: 8px;"
    );

    m_emailInput = new QLineEdit(this);
    m_emailInput->setPlaceholderText("Email address");
    m_emailInput->setClearButtonEnabled(true);
    m_emailInput->setStyleSheet(
        "QLineEdit {"
        "  border: 1.5px solid #cbd5e1; border-radius: 12px; padding: 13px 16px; background: #ffffff; font-size: 14px; color: #0f172a;"
        "}"
        "QLineEdit:focus {"
        "  border: 2px solid #3b82f6; background: #ffffff;"
        "}"
    );

    m_passwordInput = new QLineEdit(this);
    m_passwordInput->setPlaceholderText("Password");
    m_passwordInput->setEchoMode(QLineEdit::Password);
    m_passwordInput->setStyleSheet(m_emailInput->styleSheet());

    m_showPasswordCheck = new QCheckBox("Show Password", this);
    m_showPasswordCheck->setStyleSheet(
        "QCheckBox { spacing: 8px; font-size: 13px; color: #475569; font-weight: 500; }"
        "QCheckBox::indicator { width: 18px; height: 18px; border-radius: 5px; border: 1.5px solid #94a3b8; }"
        "QCheckBox::indicator:checked { background: #2563eb; border-color: #2563eb; }"
    );

    m_loginButton = new QPushButton("Sign In", this);
    m_loginButton->setCursor(Qt::PointingHandCursor);
    m_loginButton->setStyleSheet(
        "QPushButton {"
        "  background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2563eb, stop:1 #4f46e5);"
        "  color: white; border: none; border-radius: 12px; padding: 14px; font-weight: 700; font-size: 15px;"
        "}"
        "QPushButton:hover {"
        "  background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1d4ed8, stop:1 #4338ca);"
        "}"
        "QPushButton:pressed {"
        "  background: #1e40af;"
        "}"
    );

    m_errorLabel = new QLabel(this);
    m_errorLabel->setWordWrap(true);
    m_errorLabel->setStyleSheet("color: #ef4444; font-size: 13px; font-weight: 600; min-height: 18px;");

    m_registerPrompt = new QLabel("Don't have an account yet?", this);
    m_registerPrompt->setAlignment(Qt::AlignCenter);
    m_registerPrompt->setStyleSheet("color: #64748b; font-size: 13px; font-weight: 500;");

    m_createAccountButton = new QPushButton("Create an account", this);
    m_createAccountButton->setCursor(Qt::PointingHandCursor);
    m_createAccountButton->setFlat(true);
    m_createAccountButton->setStyleSheet(
        "QPushButton { color: #2563eb; font-weight: 700; font-size: 14px; border: none; padding: 4px; }"
        "QPushButton:hover { color: #1d4ed8; text-decoration: underline; }"
    );

    m_mainLayout->addWidget(m_titleLabel);
    m_mainLayout->addWidget(m_subtitleLabel);
    m_mainLayout->addWidget(m_emailInput);
    m_mainLayout->addWidget(m_passwordInput);
    m_mainLayout->addWidget(m_showPasswordCheck);
    m_mainLayout->addWidget(m_loginButton);
    m_mainLayout->addWidget(m_errorLabel);
    m_mainLayout->addSpacing(8);
    m_mainLayout->addWidget(m_registerPrompt);
    m_mainLayout->addWidget(m_createAccountButton, 0, Qt::AlignCenter);
    m_mainLayout->addStretch();

    connect(m_loginButton, &QPushButton::clicked, this, &LoginWindow::handleLogin);
    connect(m_showPasswordCheck, &QCheckBox::toggled, this, &LoginWindow::togglePasswordVisibility);
    connect(m_createAccountButton, &QPushButton::clicked, this, &LoginWindow::openRegister);

    setStyleSheet(
        "QMainWindow { background: #f8fafc; }"
        "QLabel { color: #0f172a; }"
    );
}

void LoginWindow::handleLogin()
{
    QString errorMessage;
    const bool ok = m_authService.loginUser(m_emailInput->text(), m_passwordInput->text(), errorMessage);
    if (!ok) {
        m_errorLabel->setText(errorMessage);
        return;
    }

    MainWindow* mainWindow = new MainWindow(m_authService, this);
    mainWindow->show();
    hide();
}

void LoginWindow::togglePasswordVisibility(bool checked)
{
    m_passwordInput->setEchoMode(checked ? QLineEdit::Normal : QLineEdit::Password);
}

void LoginWindow::openRegister()
{
    auto* registerWindow = new RegisterWindow(m_authService, this);
    registerWindow->show();
    hide();
}
