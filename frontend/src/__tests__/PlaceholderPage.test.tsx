import { render, screen } from '@testing-library/react';
import { I18nextProvider } from 'react-i18next';
import i18n from '@/i18n';
import PlaceholderPage from '@/pages/PlaceholderPage';

describe('PlaceholderPage', () => {
  it('renders the translated title and description', () => {
    render(
      <I18nextProvider i18n={i18n}>
        <PlaceholderPage titleKey="nav.ideas" description="Coming soon" />
      </I18nextProvider>,
    );
    expect(screen.getAllByText(/Ideas/i).length).toBeGreaterThan(0);
    expect(screen.getByText(/Coming soon/i)).toBeInTheDocument();
  });
});
