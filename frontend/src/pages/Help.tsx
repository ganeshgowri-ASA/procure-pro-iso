import {
  HelpCircle,
  Book,
  MessageCircle,
  Video,
  FileText,
  Mail,
  ExternalLink,
  Search,
} from 'lucide-react';
import { Card, Button } from '../components/ui';

export default function Help() {
  const resources = [
    {
      icon: Book,
      title: 'Documentation',
      description: 'Comprehensive guides and API references',
      link: '#',
      color: 'text-blue-500',
      bg: 'bg-blue-50',
    },
    {
      icon: Video,
      title: 'Video Tutorials',
      description: 'Step-by-step video guides',
      link: '#',
      color: 'text-red-500',
      bg: 'bg-red-50',
    },
    {
      icon: MessageCircle,
      title: 'Community Forum',
      description: 'Connect with other users',
      link: '#',
      color: 'text-green-500',
      bg: 'bg-green-50',
    },
    {
      icon: FileText,
      title: 'Release Notes',
      description: 'Latest updates and changes',
      link: '#',
      color: 'text-purple-500',
      bg: 'bg-purple-50',
    },
  ];

  const faqs = [
    {
      question: 'How do I create a new RFQ?',
      answer:
        'Navigate to RFQ Management, click "Create RFQ", fill in the required details, add items, and select vendors to invite.',
    },
    {
      question: 'How do I evaluate vendor bids?',
      answer:
        'After receiving bids, go to Technical Evaluation to score vendors against CTQ parameters, then use Commercial Evaluation for price comparison.',
    },
    {
      question: 'Can I export reports to Excel?',
      answer:
        'Yes, all tables and reports have an Export button that allows you to download data in Excel or PDF format.',
    },
    {
      question: 'How do I add a new vendor?',
      answer:
        'Go to Vendor Management, click "Add Vendor", fill in the company details, certifications, and contact information.',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="p-2 bg-purple-50 rounded-lg">
          <HelpCircle className="text-purple-brand" size={24} />
        </div>
        <div>
          <h2 className="text-xl font-bold text-gray-900">Help & Support</h2>
          <p className="text-sm text-gray-500">Find answers and get assistance</p>
        </div>
      </div>

      {/* Search */}
      <Card>
        <div className="text-center py-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">How can we help you?</h3>
          <div className="max-w-lg mx-auto relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              placeholder="Search for help articles..."
              className="w-full pl-12 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-brand focus:border-transparent outline-none"
            />
          </div>
        </div>
      </Card>

      {/* Resources Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {resources.map((resource, index) => (
          <Card
            key={index}
            className="cursor-pointer hover:shadow-lg transition-shadow text-center"
          >
            <div className={`w-12 h-12 mx-auto rounded-lg ${resource.bg} flex items-center justify-center mb-4`}>
              <resource.icon className={resource.color} size={24} />
            </div>
            <h3 className="font-semibold text-gray-900 mb-1">{resource.title}</h3>
            <p className="text-sm text-gray-500 mb-3">{resource.description}</p>
            <a
              href={resource.link}
              className="inline-flex items-center text-sm text-purple-brand hover:text-purple-deep"
            >
              Learn more <ExternalLink size={14} className="ml-1" />
            </a>
          </Card>
        ))}
      </div>

      {/* FAQs */}
      <Card>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Frequently Asked Questions</h3>
        <div className="space-y-4">
          {faqs.map((faq, index) => (
            <details
              key={index}
              className="group border border-gray-200 rounded-lg"
            >
              <summary className="flex items-center justify-between p-4 cursor-pointer font-medium text-gray-900 hover:bg-gray-50 rounded-lg">
                {faq.question}
                <span className="ml-4 text-gray-400 group-open:rotate-180 transition-transform">
                  ▼
                </span>
              </summary>
              <div className="px-4 pb-4 text-sm text-gray-600">
                {faq.answer}
              </div>
            </details>
          ))}
        </div>
      </Card>

      {/* Contact Support */}
      <Card className="bg-gradient-to-r from-purple-50 to-blue-50 border-none">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-white rounded-lg shadow-sm">
              <Mail className="text-purple-brand" size={24} />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">Need more help?</h3>
              <p className="text-sm text-gray-600">
                Our support team is available Monday-Friday, 9AM-6PM EST
              </p>
            </div>
          </div>
          <Button>Contact Support</Button>
        </div>
      </Card>
    </div>
  );
}
