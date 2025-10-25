# Changelog

## [1.1.0] - 2024-01-XX

### Added
- Telegram Stars payment system integration
- Paid requests balance system  
- Daily free requests reset (5 per day)
- Three payment packages: 15⭐/3req, 45⭐/10req, 80⭐/20req

### Changed
- Migrated from global handlers to router-based architecture
- Updated database models with free/paid requests tracking

### Fixed
- Payment callback conflicts resolved
- Invoice creation with correct Stars amounts