#pragma once

#include <QWidget>
#include <QVBoxLayout>
#include <QLabel>
#include <QFormLayout>

#include "services/AuthenticationService.h"

class ProfileWidget : public QWidget
{
    Q_OBJECT
public:
    explicit ProfileWidget(AuthenticationService& authService, QWidget* parent = nullptr);

private:
    AuthenticationService& m_authService;
    QVBoxLayout* m_layout;
    QLabel* m_title;
    QLabel* m_usernameLabel;
    QLabel* m_emailLabel;
    QLabel* m_memberSinceLabel;
    QLabel* m_activityTitle;
};
