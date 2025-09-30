import { render, screen, fireEvent } from '@testing-library/react'
import HackathonCard from '../HackathonCard'
import { Hackathon } from '@/types'

const mockHackathon: Hackathon = {
  id: '1',
  title: 'Test Hackathon',
  description: 'A test hackathon for testing purposes',
  short_description: 'Test hackathon',
  organizer: 'Test Org',
  website_url: 'https://test.com',
  registration_url: 'https://test.com/register',
  location: 'Test City',
  is_online: false,
  is_hybrid: false,
  prize_money: 10000,
  max_team_size: 4,
  difficulty_level: 'Intermediate',
  categories: ['AI/ML', 'Web Development'],
  technologies: ['Python', 'React'],
  source_platform: 'test',
  source_id: 'test-123',
  is_active: true,
  start_date: '2024-06-01T00:00:00Z',
  end_date: '2024-06-03T00:00:00Z',
  registration_deadline: '2024-05-25T00:00:00Z',
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
}

describe('HackathonCard Component', () => {
  it('renders hackathon information correctly', () => {
    render(<HackathonCard hackathon={mockHackathon} />)

    expect(screen.getByText('Test Hackathon')).toBeInTheDocument()
    expect(screen.getByText('by Test Org')).toBeInTheDocument()
    expect(screen.getByText('Test hackathon')).toBeInTheDocument()
    expect(screen.getByText('$10,000')).toBeInTheDocument()
    expect(screen.getByText('Intermediate')).toBeInTheDocument()
  })

  it('displays categories correctly', () => {
    render(<HackathonCard hackathon={mockHackathon} />)

    expect(screen.getByText('AI/ML')).toBeInTheDocument()
    expect(screen.getByText('Web Development')).toBeInTheDocument()
  })

  it('shows online badge when hackathon is online', () => {
    const onlineHackathon = { ...mockHackathon, is_online: true }
    render(<HackathonCard hackathon={onlineHackathon} />)

    expect(screen.getByText('Online')).toBeInTheDocument()
  })

  it('handles favorite button click', () => {
    const onFavorite = jest.fn()
    render(
      <HackathonCard
        hackathon={mockHackathon}
        onFavorite={onFavorite}
        isFavorited={false}
      />
    )

    const favoriteButton = screen.getByRole('button', { name: /favorite/i })
    fireEvent.click(favoriteButton)

    expect(onFavorite).toHaveBeenCalledWith('1')
  })

  it('shows favorited state correctly', () => {
    render(
      <HackathonCard
        hackathon={mockHackathon}
        onFavorite={jest.fn()}
        isFavorited={true}
      />
    )

    const favoriteButton = screen.getByRole('button', { name: /favorite/i })
    expect(favoriteButton).toHaveClass('text-red-500')
  })

  it('displays deadline soon badge when appropriate', () => {
    const soonDeadlineHackathon = {
      ...mockHackathon,
      registration_deadline: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000).toISOString() // 2 days from now
    }

    render(<HackathonCard hackathon={soonDeadlineHackathon} />)

    expect(screen.getByText('Deadline Soon')).toBeInTheDocument()
  })

  it('truncates categories when there are many', () => {
    const manyCategories = {
      ...mockHackathon,
      categories: ['AI/ML', 'Web Development', 'Mobile', 'Blockchain', 'IoT']
    }

    render(<HackathonCard hackathon={manyCategories} />)

    expect(screen.getByText('+2 more')).toBeInTheDocument()
  })

  it('handles missing optional fields gracefully', () => {
    const minimalHackathon = {
      ...mockHackathon,
      organizer: undefined,
      short_description: undefined,
      categories: undefined,
      prize_money: undefined,
    }

    render(<HackathonCard hackathon={minimalHackathon} />)

    expect(screen.getByText('Test Hackathon')).toBeInTheDocument()
    expect(screen.queryByText('by')).not.toBeInTheDocument()
  })
})