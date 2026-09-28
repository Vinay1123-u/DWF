#pragma once

#include <QWidget>
#include <QVBoxLayout>
#include <QLabel>
#include <QRadioButton>
#include <QButtonGroup>

class SettingsWidget : public QWidget
{
    Q_OBJECT
public:
    explicit SettingsWidget(QWidget* parent = nullptr);

private:
    QVBoxLayout* m_layout;
    QLabel* m_title;
    QLabel* m_themeLabel;
    QRadioButton* m_lightButton;
    QRadioButton* m_darkButton;
    QRadioButton* m_systemButton;
    QButtonGroup* m_themeGroup;
    QLabel* m_versionLabel;
};
