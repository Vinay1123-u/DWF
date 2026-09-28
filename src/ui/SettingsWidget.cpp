#include "ui/SettingsWidget.h"

#include <QVBoxLayout>

SettingsWidget::SettingsWidget(QWidget* parent)
    : QWidget(parent)
{
    m_layout = new QVBoxLayout(this);
    m_layout->setContentsMargins(32, 32, 32, 32);
    m_layout->setSpacing(12);

    m_title = new QLabel("Settings", this);
    m_title->setStyleSheet("font-size: 26px; font-weight: 700;");

    m_themeLabel = new QLabel("Theme", this);
    m_themeLabel->setStyleSheet("font-size: 18px; font-weight: 600;");

    m_lightButton = new QRadioButton("Light", this);
    m_darkButton = new QRadioButton("Dark", this);
    m_systemButton = new QRadioButton("System", this);
    m_themeGroup = new QButtonGroup(this);
    m_themeGroup->addButton(m_lightButton, 0);
    m_themeGroup->addButton(m_darkButton, 1);
    m_themeGroup->addButton(m_systemButton, 2);

    m_versionLabel = new QLabel("Dictionary Word Finder\nVersion 1.0.0", this);
    m_versionLabel->setStyleSheet("font-size: 15px; color: #6b7280;");

    m_layout->addWidget(m_title);
    m_layout->addWidget(m_themeLabel);
    m_layout->addWidget(m_lightButton);
    m_layout->addWidget(m_darkButton);
    m_layout->addWidget(m_systemButton);
    m_layout->addWidget(m_versionLabel);
    m_layout->addStretch();

    m_lightButton->setChecked(true);
}
