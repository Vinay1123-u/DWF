#include "ui/ProfileWidget.h"

ProfileWidget::ProfileWidget(AuthenticationService& authService, QWidget* parent)
    : QWidget(parent), m_authService(authService)
{
    m_layout = new QVBoxLayout(this);
    m_layout->setContentsMargins(32, 32, 32, 32);
    m_layout->setSpacing(14);

    m_title = new QLabel("Profile", this);
    m_title->setStyleSheet("font-size: 26px; font-weight: 700;");

    m_usernameLabel = new QLabel("Username\n" + authService.currentUsername(), this);
    m_usernameLabel->setStyleSheet("font-size: 18px; font-weight: 600;");
    m_emailLabel = new QLabel("Email\n" + authService.currentEmail(), this);
    m_emailLabel->setStyleSheet("font-size: 16px;");
    m_memberSinceLabel = new QLabel("Member Since\nSeptember 2026", this);
    m_memberSinceLabel->setStyleSheet("font-size: 16px;");

    m_activityTitle = new QLabel("Activity", this);
    m_activityTitle->setStyleSheet("font-size: 20px; font-weight: 700;");

    m_layout->addWidget(m_title);
    m_layout->addWidget(m_usernameLabel);
    m_layout->addWidget(m_emailLabel);
    m_layout->addWidget(m_memberSinceLabel);
    m_layout->addWidget(m_activityTitle);
    m_layout->addStretch();
}
